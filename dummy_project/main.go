package main
import (
	"unsafe"
	"fmt"
)



func main() {
	var a = 1
	var x = unsafe.Pointer(a)
	fmt.Println(unsafe.Sizeof(x))
}
