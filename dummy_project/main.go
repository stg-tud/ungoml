package main

import (
	"fmt"
	"unsafe"
)

func main() {
	var x = 0
	fmt.Println(unsafe.Sizeof(x))
}
