#!/bin/bash

# Store the HOST_IP in env-docker-compose.env, and
# Run docker-compose.yml

# TODO: resolve why this does not match settings > network & internet > status > properties: IPV4
$env= "HOST_IP=" + (Get-NetIPAddress -AddressFamily IPV4 -InterfaceAlias Ethernet).IPAddress

# Write-Output "Debug - env: " $env
Set-Content -Path ".\env-docker-compose.env" -Value $env

Write-Output ""
get-content .\env-docker-compose.env
Write-Output ""
$proceed = Read-Host -Prompt "Verify IP location above, and press RETURN to proceed> "

Write-Output ""
if (Test-Path -Path "www") {
    Write-Output " "
    Write-Output "\n... starting"
    Write-Output " "
} else {
    Write-Output " "
    Write-Output "www & etc files missing - see readme"
    Write-Output " "
    exit 1
}

# throw "debug stop"

Push-Location ../../
# ls  # verify project root docker-compose --env-file project/myproject/.env up
# https://stackoverflow.com/questions/65484277/access-env-file-variables-in-docker-compose-file

docker-compose -f ./devops/docker-compose/docker-compose.yml --env-file ./devops/docker-compose/env-docker-compose.env up

Pop-Location