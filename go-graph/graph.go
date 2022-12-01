package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"

	"gonum.org/v1/gonum/graph/simple"
)

type GraphManager struct {
	graph  *simple.DirectedGraph
	ogData jsonGraph
}

func (gm *GraphManager) jsonFromFile(file string) {
	gm.graph = simple.NewDirectedGraph()
	data, err := os.Open(file)
	if err != nil {
		fmt.Println(err)
	}

	bytes, _ := ioutil.ReadAll(data)
	json.Unmarshal(bytes, &gm.ogData)

	// add Nodes
	for _, node := range gm.ogData.Nodes {
		n := simple.Node(node.ID)
		gm.graph.AddNode(n)
	}

	// add Edges
	for _, edge := range gm.ogData.Edges {
		gm.graph.NewEdge(
			simple.Node(edge.From), // From
			simple.Node(edge.To))   // To
	}
}

type GoM struct {
	ogData  jsonGraph
	graph   *simple.DirectedGraph
	simpleG *simple.DirectedGraph
}

func (g *GoM) init(file string) {
	g.graph = simple.NewDirectedGraph()
	data, err := os.Open(file)
	if err != nil {
		fmt.Println(err)
	}

	bytes, _ := ioutil.ReadAll(data)
	json.Unmarshal(bytes, &g.ogData)

	// add Nodes
	for _, node := range g.ogData.Nodes {
		n := simple.Node(node.ID)
		g.graph.AddNode(n)
	}

	// add Edges
	for _, edge := range g.ogData.Edges {
		g.graph.NewEdge(
			simple.Node(edge.From), // From
			simple.Node(edge.To))   // To
	}

	acyclic := func(_g simple.DirectedGraph, cn simple.Node, visited map[simple.Node]simple.Node) {
		_g.hasN
	}
}
