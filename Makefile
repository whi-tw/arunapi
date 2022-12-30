go_files := $(shell git ls-files '*.go') go.mod go.sum
git_version := $(shell git describe --tags)

arunapi: ${go_files}
	CGO_ENABLED=0 go build -o arunapi -ldflags "-X main.Version=${git_version}"