import stripe

stripe.api_key = 'sk_test_51PbqQGD93W15USiaMasDyqPJtIs1UpgSuLVdPhvxmZ8bYf06KiOils2Qeypque0ZZpjMHqzeQ1LMzHg0ADzjDKby00qL3TIkqb'

# Créer un produit
product = stripe.Product.create(
    name="Daily Subscription",
)

# Créer un prix récurrent pour le produit
price = stripe.Price.create(
    unit_amount=2000,  # Montant en cents
    currency="usd",
    recurring={"interval": "day"},
    product=product.id,
)

print(f"Created product: {product.id}")
print(f"Created price: {price.id}")