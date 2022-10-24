package main

import (
	"encoding/json"
	"fmt"
	"go/build"
	"go/types"
	"path/filepath"
	"strings"

	"golang.org/x/tools/go/callgraph"
	"golang.org/x/tools/go/ssa"
)

func isSynthetic(edge *callgraph.Edge) bool {
	return edge.Caller.Func.Pkg == nil || edge.Callee.Func.Synthetic != ""
}

func inStd(node *callgraph.Node) bool {
	pkg, _ := build.Import(node.Func.Pkg.Pkg.Path(), "", 0)
	return pkg.Goroot
}

func printOutputJson(
	prog *ssa.Program,
	mainPkg *ssa.Package,
	cg *callgraph.Graph,
	focusPkg *types.Package,
	limitPaths,
	ignorePaths,
	includePaths []string,
	groupBy []string,
	nostd,
	nointer bool,
) ([]byte, error) {
	var groupType, groupPkg bool
	for _, g := range groupBy {
		switch g {
		case "pkg":
			groupPkg = true
		case "type":
			groupType = true
		}
	}
	cg.DeleteSyntheticNodes()

	nodeMap := make(map[string]*jsonNode)
	edgeMap := make(map[string]*jsonEdge)
	pkgMap := make(map[string]*jsonPkg)

	var (
		nodes []*jsonNode
		edges []*jsonEdge
		pkgs  []*jsonPkg
	)

	var isFocused = func(edge *callgraph.Edge) bool {
		caller := edge.Caller
		callee := edge.Callee
		if focusPkg != nil && (caller.Func.Pkg.Pkg.Path() == focusPkg.Path() || callee.Func.Pkg.Pkg.Path() == focusPkg.Path()) {
			return true
		}
		fromFocused := false
		toFocused := false
		for _, e := range caller.In {
			if !isSynthetic(e) && focusPkg != nil &&
				e.Caller.Func.Pkg.Pkg.Path() == focusPkg.Path() {
				fromFocused = true
				break
			}
		}
		for _, e := range callee.Out {
			if !isSynthetic(e) && focusPkg != nil &&
				e.Callee.Func.Pkg.Pkg.Path() == focusPkg.Path() {
				toFocused = true
				break
			}
		}
		if fromFocused && toFocused {
			logf("edge semi-focus: %s", edge)
			return true
		}
		return false
	}

	var inIncludes = func(node *callgraph.Node) bool {
		pkgPath := node.Func.Pkg.Pkg.Path()
		for _, p := range includePaths {
			if strings.HasPrefix(pkgPath, p) {
				return true
			}
		}
		return false
	}

	var inLimits = func(node *callgraph.Node) bool {
		pkgPath := node.Func.Pkg.Pkg.Path()
		for _, p := range limitPaths {
			if strings.HasPrefix(pkgPath, p) {
				return true
			}
		}
		return false
	}

	var inIgnores = func(node *callgraph.Node) bool {
		pkgPath := node.Func.Pkg.Pkg.Path()
		for _, p := range ignorePaths {
			if strings.HasPrefix(pkgPath, p) {
				return true
			}
		}
		return false
	}

	var isInter = func(edge *callgraph.Edge) bool {
		// caller := edge.Caller
		callee := edge.Callee
		if callee.Func.Object() != nil && !callee.Func.Object().Exported() {
			return true
		}
		return false
	}

	count := 0
	err := callgraph.GraphVisitEdges(cg, func(edge *callgraph.Edge) error {
		count++

		caller := edge.Caller
		callee := edge.Callee

		posCaller := prog.Fset.Position(caller.Func.Pos())
		posCallee := prog.Fset.Position(callee.Func.Pos())
		posEdge := prog.Fset.Position(edge.Pos())
		// fileCaller := fmt.Sprintf("%s:%d", posCaller.Filename, posCaller.Line)
		// filenameCaller := filepath.Base(posCaller.Filename)

		// omit synthetic calls
		if isSynthetic(edge) {
			return nil
		}

		callerPkg := caller.Func.Pkg.Pkg
		calleePkg := callee.Func.Pkg.Pkg

		// focus specific pkg
		if focusPkg != nil &&
			!isFocused(edge) {
			return nil
		}

		// omit std
		if nostd &&
			(inStd(caller) || inStd(callee)) {
			return nil
		}

		// omit inter
		if nointer && isInter(edge) {
			return nil
		}

		include := false
		// include path prefixes
		if len(includePaths) > 0 &&
			(inIncludes(caller) || inIncludes(callee)) {
			// logf("include: %s -> %s", caller, callee)
			include = true
		}

		if !include {
			// limit path prefixes
			if len(limitPaths) > 0 &&
				(!inLimits(caller) || !inLimits(callee)) {
				// logf("NOT in limit: %s -> %s", caller, callee)
				return nil
			}

			// ignore path prefixes
			if len(ignorePaths) > 0 &&
				(inIgnores(caller) || inIgnores(callee)) {
				// logf("IS ignored: %s -> %s", caller, callee)
				return nil
			}
		}

		// var buf bytes.Buffer
		// data, _ := json.MarshalIndent(caller.Func, "", " ")
		//logf("call node: %s -> %s\n %v", caller, callee, string(data))
		// logf("call node: %s -> %s (%s -> %s) %v\n", caller.Func.Pkg, callee.Func.Pkg, caller, callee, filenameCaller)

		var sprintNode = func(node *callgraph.Node, isCaller bool) *jsonNode {
			// only once
			key := node.Func.String()
			pkgKey := node.Func.Pkg.Pkg.Name()
			var decPos *jsonPos

			if isCaller {
				decPos = &jsonPos{
					Name: filepath.Base(posCaller.Filename),
					Line: posCaller.Line,
				}
			} else {
				decPos = &jsonPos{
					Name: filepath.Base(posCallee.Filename),
					Line: posCallee.Line,
				}
			}

			if _, ok := pkgMap[pkgKey]; !ok {
				pkgMap[pkgKey] = &jsonPkg{
					Path: node.Func.Pkg.Pkg.Path(),
					Name: node.Func.Pkg.Pkg.Name(),
				}
			}

			if n, ok := nodeMap[key]; ok {
				return n
			}

			// is focused
			isFocused := focusPkg != nil &&
				node.Func.Pkg.Pkg.Path() == focusPkg.Path()

			// node label
			label := node.Func.RelString(node.Func.Pkg.Pkg)

			// func signature
			sign := node.Func.Signature
			if node.Func.Parent() != nil {
				sign = node.Func.Parent().Signature
			}

			// omit type from label
			if groupType && sign.Recv() != nil {
				parts := strings.Split(label, ".")
				label = parts[len(parts)-1]
			}

			pkg, _ := build.Import(node.Func.Pkg.Pkg.Path(), "", 0)

			// include pkg name
			if !groupPkg && !isFocused {
				label = fmt.Sprintf("%s\n%s", node.Func.Pkg.Pkg.Name(), label)
			}

			// get Parameter Info
			funcParams := []*map[string]string{}

			for _, p := range node.Func.Params {
				fParam := map[string]string{}
				fParam["name"] = p.Name()
				fParam["type"] = p.Type().String()
				funcParams = append(funcParams, &fParam)
			}

			nodeAttrs := &jsonAttrs{
				Name:      node.Func.Name(),
				Label:     label,
				Pos:       decPos,
				IsFocused: isFocused,
				Params:    funcParams,
				PkgInRoot: pkg.Goroot,
				Pkg:       node.Func.Pkg.Pkg.Name(),
			}

			n := &jsonNode{
				ID:    node.ID,
				Attrs: nodeAttrs,
			}

			nodes = append(nodes, n)

			nodeMap[key] = n
			return n
		}
		callerNode := sprintNode(edge.Caller, true)
		calleeNode := sprintNode(edge.Callee, false)

		// edges
		attrs := make(dotAttrs)

		edgeIsDynamic := false
		edgeIsGo := false
		edgeIsDefer := false
		edgeIsOutside := false

		// dynamic call
		if edge.Site != nil && edge.Site.Common().StaticCallee() == nil {
			attrs["style"] = "dashed"
			edgeIsDynamic = true
		}

		// go & defer calls
		switch edge.Site.(type) {
		case *ssa.Go:
			attrs["arrowhead"] = "normalnoneodot"
			edgeIsGo = true
		case *ssa.Defer:
			attrs["arrowhead"] = "normalnoneodiamond"
			edgeIsDefer = true
		}

		// colorize calls outside focused pkg
		if focusPkg != nil &&
			(calleePkg.Path() != focusPkg.Path() || callerPkg.Path() != focusPkg.Path()) {
			attrs["color"] = "saddlebrown"
			edgeIsOutside = true
		}

		edgePos := &jsonPos{
			Name: filepath.Base(posEdge.Filename),
			Line: posEdge.Line,
		}

		// omit duplicate calls, except for tooltip enhancements
		key := fmt.Sprintf("%s = %s => %s", caller.Func, edge.Description(), callee.Func)
		if _, ok := edgeMap[key]; !ok {
			e := &jsonEdge{
				From: callerNode.ID,
				To:   calleeNode.ID,
				Attrs: &jsonEdgeAttrs{
					IsDynamic: edgeIsDynamic,
					IsGo:      edgeIsGo,
					IsDefer:   edgeIsDefer,
					IsOutside: edgeIsOutside,
					Pos:       edgePos,
				},
			}
			edgeMap[key] = e
		}

		return nil
	})
	if err != nil {
		return nil, err
	}

	for _, e := range edgeMap {
		edges = append(edges, e)
	}

	for _, p := range pkgMap {
		pkgs = append(pkgs, p)
	}

	jsonCG := &jsonGraph{
		Root:     cg.Root.Func.String(),
		Nodes:    nodes,
		Edges:    edges,
		Packages: pkgs,
	}

	return json.MarshalIndent(jsonCG, "", " ")
}
