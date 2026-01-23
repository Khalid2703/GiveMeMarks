#!/bin/bash
# Quick Fix Script for Tailwind Error

echo "🔧 Fixing Tailwind CSS Error..."
echo ""

echo "Step 1: Installing frontend dependencies..."
cd frontend
npm install

echo ""
echo "Step 2: Verifying installation..."
npm list tailwindcss postcss autoprefixer

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "Now you can run:"
echo "  npm run dev"
echo ""
echo "The error should be fixed!"
