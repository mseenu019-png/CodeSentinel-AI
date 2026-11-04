from typing import Dict

SAMPLE_REPOSITORIES: Dict[str, Dict[str, str]] = {
    "vulnerable_ecommerce": {
        "app/main.py": '''"""
E-Commerce API Entrypoint
Provides endpoints for auth, products, and order checkout.
"""
from fastapi import FastAPI, Request
from app.auth import authenticate_user, generate_jwt_token
from app.db import execute_user_query, save_log_entry
from app.orders import calculate_order_discounts, build_invoice_text

app = FastAPI(title="Storefront API", version="1.0.0")

@app.post("/login")
def login(username: str, password_hash: str):
    user = authenticate_user(username, password_hash)
    if user:
        return {"status": "success", "token": generate_jwt_token(username)}
    return {"status": "failed", "error": "Invalid credentials"}

@app.get("/search")
def search(query: str):
    # Query database for matching products
    return execute_user_query(query)

@app.post("/checkout")
def checkout(order_id: int, coupon_depth: int):
    # Calculate recursive coupon permutation discount
    discount = calculate_order_discounts(coupon_depth)
    invoice = build_invoice_text(order_id, ["Widget A", "Widget B", "Gadget Pro"])
    return {"order_id": order_id, "discount": discount, "invoice": invoice}
''',
        "app/auth.py": '''"""
Authentication Module
Handles user token creation and verification.
"""
import hashlib
import os

# CRITICAL SECURITY DEFECT: Hardcoded secret key committed in source
JWT_SECRET_KEY = "SUPER_SECRET_PRODUCTION_KEY_DO_NOT_LEAK_99881122"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy_token_99182"

def hash_user_password(password: str) -> str:
    # SECURITY VULNERABILITY: Weak MD5 hashing algorithm
    return hashlib.md5(password.encode()).hexdigest()

def authenticate_user(username: str, pass_hash: str):
    try:
        if username == "admin" and pass_hash == hash_user_password("admin123"):
            return {"user": "admin", "role": "root"}
    except Exception:
        # BUG: Silent broad exception swallow
        pass
    return None

def generate_jwt_token(username: str) -> str:
    return f"token_for_{username}_{JWT_SECRET_KEY}"
''',
        "app/db.py": '''"""
Database Access Layer
"""
import sqlite3

def get_connection():
    return sqlite3.connect("store.db")

def execute_user_query(user_input: str):
    conn = get_connection()
    cursor = conn.cursor()
    # CRITICAL SECURITY VULNERABILITY: Direct SQL Injection via f-string
    query = f"SELECT * FROM products WHERE name LIKE '%{user_input}%' OR category = '{user_input}'"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def save_log_entry(message: str):
    # BUG: Resource leak: open() not wrapped in context manager
    f = open("/var/log/ecommerce_audit.log", "a")
    f.write(message + "\\n")
''',
        "app/orders.py": '''"""
Order Processing and Invoicing Logic
"""
import time

def calculate_order_discounts(depth: int) -> int:
    """
    PERFORMANCE BOTTLENECK:
    Catastrophic Exponential Recursive Branching O(2^N).
    Notice this function is only 5 lines long, but will freeze the server for depth >= 35!
    """
    if depth <= 1:
        return 1
    return calculate_order_discounts(depth - 1) + calculate_order_discounts(depth - 2)

def build_invoice_text(order_id: int, items: list) -> str:
    """
    PERFORMANCE ISSUE:
    Quadratic string concatenation inside loop.
    Reallocates and copies memory each iteration.
    """
    summary = f"Invoice #{order_id}:\\n"
    for item in items:
        summary += f" - Item: {item} | Confirmed\\n"
    return summary

def register_custom_addon(addons=[]):
    """
    BUG: Mutable default argument (list).
    State will unintentionally persist and accumulate across calls.
    """
    addons.append(f"Addon_{len(addons)}")
    return addons
''',
        "app/utils.py": '''"""
System utilities and legacy helpers.
"""
import os
import subprocess

def print_receipt_linux(order_id: int):
    # CRITICAL SECURITY VULNERABILITY: Direct OS command injection via os.system
    os.system(f"echo Printing order receipt for {order_id} >> /tmp/printer.log")

def restart_print_spooler():
    # Subprocess with shell=True
    subprocess.run("systemctl restart cups", shell=True)
'''
    },

    "algorithm_duel_suite": {
        "fibonacci_naive.py": '''# Candidate A: 5-Line Naive Recursive Fibonacci
# Deceptively concise, but fatal O(2^N) exponential time complexity!
def fib_naive(n: int) -> int:
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

# Calling fib_naive(45) triggers over 2.2 trillion operations!
''',
        "fibonacci_optimized.py": '''# Candidate B: 10-Line Iterative Fibonacci
# Extra lines of code, but achieves optimal O(N) linear time and O(1) space!
def fib_optimized(n: int) -> int:
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr

# Calling fib_optimized(45) completes in less than 2 microseconds!
''',
        "duplicate_checker_naive.py": '''# Naive O(N^2) Quadratic Duplicate Checker
def has_duplicates_quadratic(items: list) -> bool:
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False
''',
        "duplicate_checker_hashset.py": '''# Optimized O(N) Hash Set Duplicate Checker
def has_duplicates_hashset(items: list) -> bool:
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False
'''
    },

    "fullstack_cloud_service": {
        "client/apiClient.ts": '''/**
 * Client API handler with common front-end vulnerabilities
 */
export async function loadUserData(userId: string) {
    // BUG: Missing await on fetch()
    const response = fetch(`http://api.internal-cloud.net/users/${userId}`);
    return response;
}

export function renderUserBio(elementId: string, bioHtml: string) {
    const el = document.getElementById(elementId);
    if (el) {
        // SECURITY VULNERABILITY: Cross-Site Scripting (XSS)
        el.innerHTML = bioHtml;
    }
}
''',
        "server/config.ts": '''/**
 * Cloud Configuration
 */
export const CloudConfig = {
    // CRITICAL: Hardcoded AWS Credentials
    awsAccessKey: "AKIAIOSFODNN7EXAMPLE",
    jwtSecret: "production_secret_token_jwt_9921",
    apiUrl: "http://unencrypted-insecure-api.internal.com/v1"
};
''',
        "worker/queue_processor.py": '''import os
import subprocess

def dispatch_job(job_name: str, batch_queue=[]):
    """
    BUG: Mutable default argument
    """
    batch_queue.append(job_name)
    # SECURITY: Command injection
    os.system(f"python runner.py --job {job_name}")
    return batch_queue
'''
    }
}
