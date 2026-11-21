"""Fungsi harga murni (tanpa I/O) supaya mudah diuji."""


def discount_amount(subtotal: int, percent: int) -> int:
    # Dibulatkan ke bawah: pelanggan tidak pernah ditagih lebih dari yang dijanjikan.
    return subtotal * percent // 100
