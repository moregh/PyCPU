# 🧠 Memory Map for 64KiB 8-Bit CPU System

This document outlines the full memory layout for a 64KiB RAM system with an 80x50 ASCII display.

---

## 📜 Overview

| Purpose                    | Start Address | End Address | Size (Bytes) | Description                                 |
|---------------------------|---------------|-------------|--------------|---------------------------------------------|
| Program Code & Constants  | `0x0000`      | `0x7FFF`    | 32768        | 32 KiB for executable code and static data  |
| Global Variables / Heap   | `0x8000`      | `0xDFFF`    | 24576        | Static/global variables|
| Software Stack            | `0xE000`      | `0xEDFF`    | 3584         | Stack grows downward                        |
| System Variables          | `0xEE00`      | `0xEEFF`    | 256          | Reserved for SP, flags, I/O, debug, etc.    |
| GPU Control Registers     | `0xF000`      | `0xF05F`    | 96           | Memory-mapped registers for display control |
| GPU Framebuffer (80x50)   | `0xF060`      | `0xFFFF`    | 4000         | Display buffer (80 columns × 50 rows)       |

---v

## 🧩 Detailed Map

### 🔹 Program Area

- **Address Range**: `0x0000–0x7FFF`
- **Use**: Code, constants, read-only data
- **Notes**: Execution begins at `0x0000`

---

### 🔹 Global Variables / Heap

- **Address Range**: `0x8000–0xDFFF`
- **Use**: Static variables, or managed heap (malloc/free style)
- **Size**: 24 KiB

---

### 🔹 Stack
v
- **Address Range**: `0xE000–0xEDFF`
- **Size**: 3584 bytes
- **Growth Direction**: Downward
- **Initial SP**: `0xEDFF` (top of stack)

---

### 🔹 System Variables (`0xEE00–0xEEFF`)

| Address    | Name                      | Size | Description                          |
|------------|---------------------------|------|--------------------------------------|
| `0xEE00`   | Stack Pointer Lo (SP_L)   | 1    | Low byte of 16-bit stack pointer     |
| `0xEE01`   | Stack Pointer Hi (SP_H)   | 1    | High byte of stack pointer           |
| `0xEE02`   | Frame Pointer Lo (FP_L)   | 1    | Optional: low byte of frame pointer  |
| `0xEE03`   | Frame Pointer Hi (FP_H)   | 1    | Optional: high byte of frame pointer |
| `0xEE10`   | System Flags              | 1    | Zero, carry, overflow, error flags   |
| `0xEE11`   | Exit / Error Code         | 1    | Return code from main or subroutine  |
| `0xEE40`   | Input Char                | 1    | Last input character                 |
| `0xEE41`   | Input Ready Flag          | 1    | 1 if input character available       |
| `0xEE60`   | Output Char               | 1    | Write character to output device     |
| `0xEE61`   | Output Ready Flag         | 1    | 1 if output is valid                 |
| `0xEE70`   | Breakpoint Trigger        | 1    | Write to trigger debugger breakpoint |
| `0xEE71`   | Debug Log Char            | 1    | Log stream output to debugger        |
| `0xEE80`   | Stack Base Addr Lo        | 1    | Low byte of base stack address       |
| `0xEE81`   | Stack Base Addr Hi        | 1    | High byte of base stack address      |
| `0xEE82`   | GPU Memory Start Lo       | 1    | Low byte of framebuffer base         |
| `0xEE83`   | GPU Memory Start Hi       | 1    | High byte of framebuffer base        |
| `0xEE84–0xEEFF` | —                    | —    | Reserved / Unused                    |

---

### 🔹 GPU Registers (`0xF000–0xF05F`)

| Address    | Name                  | Size | Description                         |
|------------|-----------------------|------|-------------------------------------|
| `0xF000`   | GPU Width             | 1    | Display width in characters (80)    |
| `0xF001`   | GPU Height            | 1    | Display height in characters (50)   |
| `0xF002`   | GPU Cursor Column     | 1    | X position for drawing              |
| `0xF003`   | GPU Cursor Row        | 1    | Y position for drawing              |
| `0xF004`   | GPU Mem Start X       | 1    | Viewport scroll X                   |
| `0xF005`   | GPU Mem Start Y       | 1    | Viewport scroll Y                   |
| `0xF006`   | GPU Character         | 1    | ASCII character to draw             |
| `0xF007`   | GPU Draw Trigger      | 1    | Write here to commit draw operation |
| `0xF008–0xF05F` | Reserved         | 88   | Reserved for future expansion       |

---

### 🔹 GPU Framebuffer (`0xF060–0xFFFF`)

- **Size**: 4000 bytes
- **Resolution**: 80×50 (rows × columns)
- **Each byte**: One ASCII character
- **Usage**: Write character codes directly to this region

---

## 📊 Visual Memory Map

# 🧠 Memory Map for 64KiB 8-Bit CPU System

This document defines the complete memory layout for a 64KiB RAM system with an 8-bit CPU, 16-bit addressing, software-managed stack, and an 80×50 ASCII display mapped to the top of RAM.

---

## 📘 Unified Memory Map

| Start     | End       | Size    | Purpose / Name               | Notes |
|-----------|-----------|---------|------------------------------|-------|
| `0x0000`  | `0x7FFF`  | 32 KiB  | Program Code & Constants     | Executable code, read-only data |
| `0x8000`  | `0xDFFF`  | 24 KiB  | Global Variables / Heap      | Static/global vars or heap |
| `0xE000`  | `0xEDFF`  | 3584 B  | Software Stack               | Stack grows downward from `0xEDFF` |
| `0xEE00`  | `0xEE01`  | 2 B     | Stack Pointer (SP)           | Low + High byte (16-bit) |
| `0xEE02`  | `0xEE03`  | 2 B     | Frame Pointer (optional)     | For structured stack frames |
| `0xEE10`  | `0xEE10`  | 1 B     | System Flags                 | Bitfield for flags (Z, C, etc.) |
| `0xEE11`  | `0xEE11`  | 1 B     | Exit / Error Code            | For return values or error handling |
| `0xEE40`  | `0xEE40`  | 1 B     | Input Char                   | Last input character (if used) |
| `0xEE41`  | `0xEE41`  | 1 B     | Input Ready Flag             | 1 = input available |
| `0xEE60`  | `0xEE60`  | 1 B     | Output Char                  | Write to print a character |
| `0xEE61`  | `0xEE61`  | 1 B     | Output Ready Flag            | 1 = output valid |
| `0xEE70`  | `0xEE70`  | 1 B     | Breakpoint Trigger           | Write to trigger emulator breakpoint |
| `0xEE71`  | `0xEE71`  | 1 B     | Debug Log Char               | Writes to debugger log output |
| `0xEE80`  | `0xEE81`  | 2 B     | Stack Base Address           | Useful for offset-based stack logic |
| `0xEE82`  | `0xEE83`  | 2 B     | GPU Memory Start Address     | Typically `0xF060` |
| `0xEE84`  | `0xEEFF`  | 124 B   | Reserved                     | Reserved for future use |
| `0xF000`  | `0xF000`  | 1 B     | GPU Width                    | Width in characters (typically 80) |
| `0xF001`  | `0xF001`  | 1 B     | GPU Height                   | Height in characters (typically 50) |
| `0xF002`  | `0xF002`  | 1 B     | GPU Cursor Column            | Drawing position X |
| `0xF003`  | `0xF003`  | 1 B     | GPU Cursor Row               | Drawing position Y |
| `0xF004`  | `0xF004`  | 1 B     | GPU Mem Start X              | Horizontal scroll |
| `0xF005`  | `0xF005`  | 1 B     | GPU Mem Start Y              | Vertical scroll |
| `0xF006`  | `0xF006`  | 1 B     | GPU Character                | ASCII char to draw |
| `0xF007`  | `0xF007`  | 1 B     | GPU Draw Trigger             | Write to draw character |
| `0xF008`  | `0xF05F`  | 88 B    | GPU Reserved Registers       | For future GPU expansion |
| `0xF060`  | `0xFFFF`  | 4000 B  | GPU Framebuffer (80×50)      | One byte per screen character |

---
