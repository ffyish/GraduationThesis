package main

import "fmt"

func main() {
	var gom GoM
	gom.init("rclone.json")
	for _, node := range gom.ogData.Nodes {
		fmt.Printf("%v \n", node.ID)
	}
}
