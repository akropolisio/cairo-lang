import re

from starkware.cairo.lang.compiler.preprocessor.preprocessor_test_utils import (
    strip_comments_and_linebreaks,
)
from starkware.starknet.compiler.test_utils import preprocess_str, verify_exception
from starkware.starknet.public.abi import starknet_keccak


def test_storage_var_success():
    program = preprocess_str(
        """
%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

struct A:
    member x : felt
end

struct B:
    member a : A
    member y : felt
end

func g{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    let (x) = my_var.read()
    my_var.write(value=x + 1)
    local syscall_ptr : felt* = syscall_ptr
    let (my_var2_addr) = my_var2.addr(1, 2)
    my_var2.write(1, 2, value=B(A(3), 4))
    let a = my_var2.read(1, 2)
    return ()
end

@storage_var
func my_var() -> (res : felt):
    # Comment.

end

@storage_var
func my_var2(x, y) -> (res : B):
end
"""
    )
    addr = starknet_keccak(b"my_var")
    addr2 = starknet_keccak(b"my_var2")
    expected_result = f"""\
# Code for the dummy modules.
ret
ret
ret
ret

# Implementation of g.
ap += 1
[ap] = [fp + (-5)]; ap++       # Push syscall_ptr.
[ap] = [fp + (-4)]; ap++       # Push pedersen_ptr.
[ap] = [fp + (-3)]; ap++       # Push range_check_ptr.
call rel ???                   # Call my_var.read.
[ap] = [ap + (-4)]; ap++       # Push (updated) syscall_ptr.
[ap] = [ap + (-4)]; ap++       # Push (updated) pedersen_ptr.
[ap] = [ap + (-4)]; ap++       # Push (updated) range_check_ptr.
[ap] = [ap + (-4)] + 1; ap++   # Push value.
call rel ???                   # Call my_var.write.
[fp] = [ap + (-3)]             # Copy syscall_ptr to a local variable.
[ap] = 1; ap++                 # Push 1.
[ap] = 2; ap++                 # Push 2.
call rel ???                   # Call my_var2.addr.
[ap] = [fp]; ap++              # Push syscall_ptr.
[ap] = [ap + (-4)]; ap++       # Push pedersen_ptr.
[ap] = [ap + (-4)]; ap++       # Push range_check_ptr.
[ap] = 1; ap++                 # Push 1.
[ap] = 2; ap++                 # Push 2.
[ap] = 3; ap++                 # Push 3.
[ap] = 4; ap++                 # Push 4.
call rel ???                   # Call my_var2.write.
[ap] = 1; ap++                 # Push 1.
[ap] = 2; ap++                 # Push 2.
call rel ???                   # Call my_var2.read.
[ap] = [ap + (-5)]; ap++       # Return (updated) syscall_ptr.
[ap] = [ap + (-5)]; ap++       # Return (updated) pedersen_ptr.
[ap] = [ap + (-5)]; ap++       # Return (updated) range_check_ptr.
ret

# Implementation of my_var.addr.
[ap] = [fp + (-4)]; ap++       # Return pedersen_ptr.
[ap] = [fp + (-3)]; ap++       # Return range_check_ptr.
[ap] = {addr}; ap++            # Return address.
ret

# Implementation of my_var.read.
[ap] = [fp + (-4)]; ap++       # Push pedersen_ptr.
[ap] = [fp + (-3)]; ap++       # Push range_check_ptr.
call rel ???                   # Call my_var.addr().
[ap] = [fp + (-5)]; ap++       # Push syscall_ptr.
[ap] = [ap + (-2)]; ap++       # Push address.
call rel ???                   # Call storage_read().
[ap] = [ap + (-2)]; ap++       # Return (updated) syscall_ptr.
[ap] = [ap + (-8)]; ap++       # Return (updated) pedersen_ptr.
[ap] = [ap + (-8)]; ap++       # Return (updated) range_check_ptr.
[ap] = [ap + (-4)]; ap++       # Return value.
ret

# Implementation of my_var.write.
[ap] = [fp + (-5)]; ap++       # Push range_check_ptr.
[ap] = [fp + (-4)]; ap++       # Push pedersen_ptr.
call rel ???                   # Call my_var.addr().
[ap] = [fp + (-6)]; ap++       # Push syscall_ptr.
[ap] = [ap + (-2)]; ap++       # Push address.
[ap] = [fp + (-3)]; ap++       # Push value.
call rel ???                   # Call storage_write().
[ap] = [ap + (-8)]; ap++       # Return (updated) range_check_ptr.
[ap] = [ap + (-8)]; ap++       # Return (updated) pedersen_ptr.
ret

# Implementation of my_var2.addr.
[ap] = [fp + (-6)]; ap++       # Push pedersen_ptr.
[ap] = {addr2}; ap++           # Push address.
[ap] = [fp + (-4)]; ap++       # Push x.
call rel ???                   # Call hash2(res, x).
[ap] = [fp + (-3)]; ap++       # Push y.
call rel ???                   # Call hash2(res, y).
[ap] = [fp + (-5)]; ap++       # Push range_check_ptr.
[ap] = [ap + (-2)]; ap++       # Push res.
call rel ???                   # Call normalize_address(res).
[ap] = [ap + (-6)]; ap++       # Return (updated) pedersen_ptr.
[ap] = [ap + (-3)]; ap++       # Return (updated) range_check_ptr.
[ap] = [ap + (-3)]; ap++       # Return res.
ret

# Implementation of my_var2.read.
[ap] = [fp + (-6)]; ap++       # Push pedersen_ptr .
[ap] = [fp + (-5)]; ap++       # Push range_check_ptr.
[ap] = [fp + (-4)]; ap++       # Push x.
[ap] = [fp + (-3)]; ap++       # Push y.
call rel ???                   # Call my_var.addr().
[ap] = [fp + (-7)]; ap++       # Push syscall_ptr.
[ap] = [ap + (-2)]; ap++       # Push address.
call rel ???                   # Call storage_read().
[ap] = [ap + (-2)]; ap++       # Push (updated) syscall_ptr.
[ap] = [ap + (-6)] + 1; ap++   # Push address + 1.
call rel ???                   # Call storage_read().
[ap] = [ap + (-2)]; ap++       # Return (updated) syscall_ptr.
[ap] = [ap + (-12)]; ap++      # Return (updated) pedersen_ptr.
[ap] = [ap + (-12)]; ap++      # Return (updated) range_check_ptr.
[ap] = [ap + (-8)]; ap++       # Return value (B.a.x).
[ap] = [ap + (-5)]; ap++       # Return value (B.y).
ret

# Implementation of my_var2.write.
[ap] = [fp + (-8)]; ap++       # Push pedersen_ptr.
[ap] = [fp + (-7)]; ap++       # Push range_check_ptr.
[ap] = [fp + (-6)]; ap++       # Push x.
[ap] = [fp + (-5)]; ap++       # Push y.
call rel ???                   # Call my_var.addr().
[ap] = [fp + (-9)]; ap++       # Push syscall_ptr.
[ap] = [ap + (-2)]; ap++       # Push address.
[ap] = [fp + (-4)]; ap++       # Push value.
call rel ???                   # Call storage_write().
[ap] = [ap + (-6)] + 1; ap++   # Push address.
[ap] = [fp + (-3)]; ap++       # Push value.
call rel ???                   # Call storage_write().
[ap] = [ap + (-12)]; ap++      # Return (updated) pedersen_ptr.
[ap] = [ap + (-12)]; ap++      # Return (updated) range_check_ptr.
ret
"""
    assert (
        re.sub("call rel -?[0-9]+", "call rel ???", program.format())
        == strip_comments_and_linebreaks(expected_result).lstrip()
    )


def test_storage_var_failures():
    verify_exception(
        """
@storage_var
func f() -> (res : felt):
end
""",
        """
file:?:?: @storage_var can only be used in source files that contain the "%lang starknet" directive.
@storage_var
 ^*********^
""",
    )
    verify_exception(
        """
%lang starknet
@storage_var
func f() -> (res : felt):
    return ()  # Comment.
end
""",
        """
file:?:?: Storage variables must have an empty body.
    return ()  # Comment.
    ^*******^
""",
    )
    verify_exception(
        """
%lang starknet
@storage_var
func f() -> (res : felt):
    0 = 1  # Comment.
end
""",
        """
file:?:?: Storage variables must have an empty body.
    0 = 1  # Comment.
    ^***************^
""",
    )
    verify_exception(
        """
%lang starknet
@storage_var
func f{x, y}() -> (res : felt):
end
""",
        """
file:?:?: Storage variables must have no implicit arguments.
func f{x, y}() -> (res : felt):
       ^**^
""",
    )
    verify_exception(
        """
%lang starknet
@storage_var
@invalid_decorator
func f() -> (res : felt):
end
""",
        """
file:?:?: Storage variables must have no decorators in addition to @storage_var.
@invalid_decorator
 ^***************^
""",
    )
    verify_exception(
        """
%lang starknet
@storage_var
func f(x, y : felt*) -> (res : felt):
end
""",
        """
file:?:?: Only felt arguments are supported in storage variables.
func f(x, y : felt*) -> (res : felt):
              ^***^
""",
    )
    verify_exception(
        """
%lang starknet
@storage_var
func f():
end
""",
        """
file:?:?: Storage variables must return exactly one value.
func f():
     ^
""",
    )
    verify_exception(
        """
%lang starknet
@storage_var
func f() -> (x : felt, y : felt):
end
""",
        """
file:?:?: Storage variables must return exactly one value.
func f() -> (x : felt, y : felt):
             ^****************^
""",
    )
    verify_exception(
        """
%lang starknet
@storage_var
func f() -> (x : felt*):
end
""",
        """
file:?:?: The return type of storage variables must consist of felts.
func f() -> (x : felt*):
             ^*******^
""",
    )
    verify_exception(
        """
%lang starknet

# A struct of size 10.
struct A:
    member x : (felt, felt, felt, felt, felt, felt, felt, felt, felt, felt)
end

# A struct of size 300.
struct B:
    member x : (A, A, A, A, A, A, A, A, A, A)
    member y : (A, A, A, A, A, A, A, A, A, A)
    member z : (A, A, A, A, A, A, A, A, A, A)
end

@storage_var
func f() -> (x : B):
end
""",
        """
file:?:?: The storage variable size (300) exceeds the maximum value (256).
func f() -> (x : B):
             ^***^
""",
    )


def test_storage_var_tail_call_failure():
    verify_exception(
        """
%lang starknet
%builtins pedersen range_check
from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func f() -> (x : felt):
end

@external
func test{syscall_ptr : felt*, range_check_ptr, pedersen_ptr : HashBuiltin*}() -> (x : felt):
    return f.read()
end
""",
        """
file:?:?: Cannot convert the implicit arguments of f.read to the implicit arguments of test.
    return f.read()
    ^*************^
The implicit arguments of 'f.read' were defined here:
file:?:?
    func read{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (x : felt):
              ^***************************************************************^
The implicit arguments of 'test' were defined here:
file:?:?
func test{syscall_ptr : felt*, range_check_ptr, pedersen_ptr : HashBuiltin*}() -> (x : felt):
          ^***************************************************************^
""",
    )
