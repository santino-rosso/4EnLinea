import bcrypt

class HashPassword:
    def hash_password(password: str) -> str:
        """Genera un hash de la contraseña."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(stored_hash: str, password: str) -> bool:
        """Verifica si la contraseña ingresada coincide con el hash almacenado."""
        return bcrypt.checkpw(password.encode(), stored_hash.encode())