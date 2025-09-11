applyTo: "softsynth/*_arm64.S"
title: "ARM64 Assembly Instructions"

# Copilot Instructions for ARM64 Assembly in This Project

## 1. General Conventions

- Follow the ARM64 Procedure Call Standard (AAPCS) for function arguments, return values, and register usage.
- Use `.global` to export symbols and `#define` for C/ASM symbol mapping.
- Use `PUSH_LINK_REGISTER` and `POP_LINK_REGISTER` macros to save/restore the link register in functions that call other functions.

## 2. Function Arguments and Return Values

- Integer arguments: x0, x1, x2, ...
- Floating-point arguments: s0, s1, ...
- Return values: w0 (int), s0/s1 (float).
- For C-callable functions, use the correct argument registers and convert float return values to int if needed (e.g., `fcvtzs w0, s1`).

## 3. Memory and Data

- Use `LOAD_ADDR` macro to load addresses of data symbols (for GOT/PIE safety).
- Load constants (like π) from memory, not with `fmov` (immediate floats are limited).
- Use `.data` and `.bss` for global variables and buffers.

## 5. Control Flow and Labels

- Use local labels (`1:`, `2:`) and branch with `b.cond 1f` or `b.cond 1b`.
- Use conditional instructions (`fcmp`, `b.ge`, `cbz`, etc.) for efficient branching.

## 6. Instrument and Synth Data

- Instrument data is stored in arrays; access with scaled indices (e.g., `x5, x5, lsl #2` for float arrays).
- Use `.space` for reserving buffer space in `.bss`.

## 7. Debugging

- Use LLDB for debugging:
  - Set breakpoints: `b function_name` or `b file:line`
  - Print memory: `memory read --format f --count N symbol`
  - Remove breakpoints: `br del` or `breakpoint delete`

## 8. Example Patterns

- Loading a float constant:
  ```
  LOAD_ADDR x2, pi_const
  ldr s2, [x2]
  ```
- Reducing an angle:
  ```
  fdiv s3, s1, s2
  frintm s3, s3
  fmul s3, s3, s2
  fsub s1, s1, s3
  ```
- Conditional sign flip:
  ```
  fcmp s1, #0.0
  b.ge 1f
  fneg s1, s1
  1:
  ```

## 9. File Structure

- Place all ARM64 routines in `softsynth_arm64.S` and wrappers in `softsynth_wrapper_arm64.S`.
- Use `.extern` for external symbols and `.global` for exported functions.

## 10. Compile Targets

- The compile target is Macs with Apple Silicon (ARM64/AArch64).
- Ensure all instructions and features used are valid and supported on Apple Silicon.
- Avoid legacy ARM or x86 instructions and any features not available on macOS ARM64.
