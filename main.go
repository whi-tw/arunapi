package main

import (
	"flag"
	"fmt"
	"github.com/whi-tw/arunapi/config"
	"github.com/whi-tw/arunapi/server"
	"log"
	"os"
)

var Version string = "development"

func main() {
	environment := flag.String("e", "development", "")
	flag.Usage = func() {
		fmt.Println("Usage: server -e {mode}")
		os.Exit(1)
	}
	version := flag.Bool("v")
	flag.Parse()
	err := config.LoadConfig(*environment)
	if err != nil {
		log.Fatalln(err)
	}
	server.Init()
}
