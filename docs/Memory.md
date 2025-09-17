# Memory Map for 64KiB 8-Bit CPU System

This document defines the complete memory layout for a 64KiB RAM system with an 8-bit CPU, 16-bit addressing, and an optional 80x50 ASCII display.

## Overview

The CPU emulator supports configurable RAM sizes from 4KB to 64KB. When a GPU display is enabled, it occupies the top 4000 bytes of available memory. The memory layout below assumes the maximum 64KB configuration with GPU enabled.

## Full Memory Map (64KB with GPU)

| Start     | End       | Size    | Purpose                      | Description |
|-----------|-----------|---------|------------------------------|-------------|
| `0x0000`  | `0x7FFF`  | 32 KiB  | Program Code & Constants     | Executable code, read-only data |
| `0x8000`  | `0xDFFF`  | 24 KiB  | Global Variables / Heap      | Static variables or managed heap |
| `0xE000`  | `0xEDFF`  | 3584 B  | Software Stack               | Stack grows downward from top |
| `0xEE00`  | `0xEEFF`  | 256 B   | System Variables             | Reserved for system use |
| `0xF000`  | `0xF05F`  | 96 B    | GPU Control Registers        | Display control (optional) |
| `0xF060`  | `0xFFFF`  | 4000 B  | GPU Framebuffer (80x50)      | Display buffer (optional) |

## Memory Layout Without GPU

When no GPU is present, the entire address space is available for program use:

| Start     | End       | Size    | Purpose                      |
|-----------|-----------|---------|------------------------------|
| `0x0000`  | `0xFFFF`  | 64 KiB  | Program Memory               |

## Detailed Memory Regions

### Program Code & Constants (0x0000-0x7FFF)

- **Purpose**: Executable instructions and read-only data
- **Size**: 32KB
- **Notes**: Program execution begins at address `0x0000`

### Global Variables / Heap (0x8000-0xDFFF)

- **Purpose**: Static variables, global data, or dynamically allocated memory
- **Size**: 24KB
- **Usage**: Application-specific data storage

### Software Stack (0xE000-0xEDFF)

- **Purpose**: Function call stack, local variables, return addresses
- **Size**: 3584 bytes
- **Growth**: Downward from `0xEDFF`
- **Notes**: Software-managed; no hardware stack pointer

### System Variables (0xEE00-0xEEFF)

Reserved memory region for system-level variables and I/O operations:

| Address    | Name                  | Size | Description |
|------------|-----------------------|------|-------------|
| `0xEE00`   | Stack Pointer Low     | 1    | Software stack pointer (low byte) |
| `0xEE01`   | Stack Pointer High    | 1    | Software stack pointer (high byte) |
| `0xEE02`   | Frame Pointer Low     | 1    | Optional frame pointer (low byte) |
| `0xEE03`   | Frame Pointer High    | 1    | Optional frame pointer (high byte) |
| `0xEE10`   | System Flags          | 1    | Extended system flags |
| `0xEE11`   | Exit Code             | 1    | Program exit/error code |
| `0xEE40`   | Input Character       | 1    | Last input character |
| `0xEE41`   | Input Ready Flag      | 1    | Input availability flag |
| `0xEE60`   | Output Character      | 1    | Character output register |
| `0xEE61`   | Output Ready Flag     | 1    | Output status flag |
| `0xEE70`   | Breakpoint Trigger    | 1    | Debugger breakpoint trigger |
| `0xEE71`   | Debug Log Character   | 1    | Debug output stream |
| `0xEE80`   | Stack Base Low        | 1    | Stack base address (low byte) |
| `0xEE81`   | Stack Base High       | 1    | Stack base address (high byte) |
| `0xEE82`   | GPU Start Low         | 1    | GPU memory start (low byte) |
| `0xEE83`   | GPU Start High        | 1    | GPU memory start (high byte) |
| `0xEE84`   | Reserved              | 124  | Reserved for future use |

### GPU Control Registers (0xF000-0xF05F)

Available only when GPU is enabled:

| Address    | Name                  | Size | Description |
|------------|-----------------------|------|-------------|
| `0xF000`   | Display Width         | 1    | Characters per row (typically 80) |
| `0xF001`   | Display Height        | 1    | Number of rows (typically 50) |
| `0xF002`   | Cursor Column         | 1    | Current drawing X position |
| `0xF003`   | Cursor Row            | 1    | Current drawing Y position |
| `0xF004`   | Viewport X Offset     | 1    | Horizontal scroll offset |
| `0xF005`   | Viewport Y Offset     | 1    | Vertical scroll offset |
| `0xF006`   | Draw Character        | 1    | ASCII character to draw |
| `0xF007`   | Draw Trigger          | 1    | Write to execute draw operation |
| `0xF008`   | Reserved              | 88   | Reserved for GPU expansion |

### GPU Framebuffer (0xF060-0xFFFF)

- **Purpose**: Direct character display buffer
- **Size**: 4000 bytes (80 columns x 50 rows)
- **Format**: One ASCII character code per byte
- **Layout**: Row-major order (row 0: bytes 0-79, row 1: bytes 80-159, etc.)
- **Usage**: Write ASCII values directly to display characters

## Memory Access Examples

### Assembly Language Examples

```assembly
; Write character 'A' (65) to top-left corner
LDA 65          ; Load ASCII 'A'
WMA $F060       ; Write to framebuffer position (0,0)

; Using indexed memory access
LDY $F0         ; High byte of framebuffer
LDX $60         ; Low byte of framebuffer  
LDA 72          ; ASCII 'H'
WMI             ; Write to memory[Y*256 + X]
```

### Memory Layout Notes

1. **Configurable RAM**: Actual available memory depends on CPU configuration (4KB-64KB)
2. **GPU Optional**: GPU regions only exist when Display object is provided to CPU
3. **Address Wrapping**: All memory accesses wrap within the configured RAM size
4. **Byte Ordering**: 16-bit addresses use big-endian format (high byte, low byte)

## Implementation Details

The CPU emulator automatically reserves GPU memory when a Display object is attached:

```python
# CPU without GPU - full RAM available
cpu = CPU(ram_size=64)  # 64KB RAM

# CPU with GPU - reserves top 4000 bytes for display
cpu = CPU(ram_size=64, gpu=Display(80, 50))  # 60KB + 4KB GPU
```

The GPU memory region is automatically calculated as:
- **GPU_OFFSET**: `RAM_SIZE - GPU_SIZE`
- **GPU_SIZE**: `width * height` (4000 bytes for 80x50 display)

This memory map provides a foundation for structured programming with clear separation between code, data, stack, and display regions.