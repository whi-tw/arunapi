package main

import (
	"flag"
	"fmt"
	"github.com/whi-tw/arunapi/config"
	"github.com/whi-tw/arunapi/server"
	"log"
	"os"
)

func main() {
	environment := flag.String("e", "development", "")
	flag.Usage = func() {
		fmt.Println("Usage: server -e {mode}")
		os.Exit(1)
	}
	flag.Parse()
	err := config.LoadConfig(*environment)
	if err != nil {
		log.Fatalln(err)
	}
	server.Init()
}
