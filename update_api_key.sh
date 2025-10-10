#!/bin/bash
# Quick script to update OpenAI API key

echo "🔑 Update OpenAI API Key"
echo "========================"
echo ""
echo "Current key: $(grep OPENAI_API_KEY .env | cut -d'=' -f2 | cut -c1-15)..."
echo ""
read -p "Enter your new OpenAI API key (starts with sk-proj- or sk-): " NEW_KEY
echo ""

if [[ -z "$NEW_KEY" ]]; then
    echo "❌ No key provided. Exiting."
    exit 1
fi

if [[ ! "$NEW_KEY" =~ ^sk- ]]; then
    echo "⚠️  Warning: Key doesn't start with 'sk-'. Are you sure this is correct?"
    read -p "Continue anyway? (y/n): " CONFIRM
    if [[ "$CONFIRM" != "y" ]]; then
        echo "❌ Cancelled."
        exit 1
    fi
fi

# Backup current .env
cp .env .env.backup
echo "✅ Backed up .env to .env.backup"

# Update the key
if grep -q "OPENAI_API_KEY=" .env; then
    # Replace existing key
    sed -i '' "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$NEW_KEY|" .env
    echo "✅ Updated OPENAI_API_KEY in .env"
else
    # Add new key
    echo "OPENAI_API_KEY=$NEW_KEY" >> .env
    echo "✅ Added OPENAI_API_KEY to .env"
fi

echo ""
echo "🎉 API Key updated successfully!"
echo ""
echo "Verify with:"
echo "  grep OPENAI_API_KEY .env"
echo ""
echo "Test connectivity:"
echo "  make test-connectivity"

