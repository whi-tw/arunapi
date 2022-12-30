package main

import "github.com/whi-tw/arunapi/cmd"

var Version string = "development"

func main() {
	_ = cmd.Execute(Version)
}
