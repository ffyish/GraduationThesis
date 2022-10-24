package main

type jsonAttrs struct {
	Name      string               `json:"name"`
	Label     string               `json:"label"`
	Pos       *jsonPos             `json:"pos"`
	IsFocused bool                 `json:"isFocused"`
	Params    []*map[string]string `json:"params"`
	PkgInRoot bool                 `json:"pkgInRoot"`
	Pkg       string               `json:"pkg"`
}

type jsonEdgeAttrs struct {
	IsDynamic bool     `json:"isDynamic"`
	IsGo      bool     `json:"isGo"`
	IsDefer   bool     `json:"isDefer"`
	IsOutside bool     `json:"isOutside"`
	Pos       *jsonPos `json:"pos"`
}

type jsonNode struct {
	ID    int        `json:"id"`
	Attrs *jsonAttrs `json:"attrs"`
}

type jsonEdge struct {
	From  int            `json:"from"`
	To    int            `json:"to"`
	Attrs *jsonEdgeAttrs `json:"attrs"`
}

type jsonPos struct {
	Name string `json:"name"`
	Line int    `json:"line"`
}

type jsonPkg struct {
	Path string `json:"path"`
	Name string `json:"name"`
}

type jsonGraph struct {
	Root     string
	Nodes    []*jsonNode
	Edges    []*jsonEdge
	Packages []*jsonPkg
}
