python3 - << 'EOF'
import bcrypt
pw = b\"ControlMorado12#\"
print(bcrypt.hashpw(pw, bcrypt.gensalt()).decode())
EOF