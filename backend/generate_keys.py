"""
Generate secure secret keys for production deployment
Run this script to generate JWT_SECRET_KEY and SECRET_KEY
"""
import secrets

print("\n" + "="*60)
print("🔐 SECURE KEY GENERATOR FOR RENDER DEPLOYMENT")
print("="*60)

print("\n📋 Copy these to your Render Environment Variables:\n")

print("JWT_SECRET_KEY:")
print(secrets.token_urlsafe(32))

print("\nSECRET_KEY:")
print(secrets.token_urlsafe(32))

print("\n" + "="*60)
print("⚠️  IMPORTANT: Keep these keys secret!")
print("   Never commit them to GitHub or share publicly")
print("="*60 + "\n")

print("📝 How to use:")
print("   1. Copy JWT_SECRET_KEY value")
print("   2. In Render dashboard: Backend → Environment")
print("   3. Add: JWT_SECRET_KEY = <paste-value>")
print("   4. Repeat for SECRET_KEY")
print("   5. Save and deploy\n")
