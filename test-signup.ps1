$body = @{
    email = "alice@test.com"
    password = "Pass1234"
    name = "Alice"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:3002/api/auth/sign-up/email" -Method POST -ContentType "application/json" -Body $body
$response | ConvertTo-Json
