NASM   := nasm
LD     := ld
FORMAT := elf32

TARGET := fork_and_go
SRC    := $(TARGET).asm
OBJ    := $(TARGET).o

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJ)
	$(LD) -m elf_i386 $(OBJ) -o $@

$(OBJ): $(SRC)
	$(NASM) -f $(FORMAT) $(SRC) -o $@

clean:
	rm -f $(OBJ) $(TARGET)
