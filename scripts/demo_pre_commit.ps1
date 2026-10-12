# Демонстраційний скрипт тестування pre-commit хуків
Write-Host "=== 1. Перевірка статусу pre-commit ===" -ForegroundColor Cyan
pre-commit run --all-files

Write-Host "`n=== 2. Створення тестового файлу з навмисною синтаксичною помилкою ===" -ForegroundColor Yellow
$badCode = @"
def broken_zombie_function(
    print("Syntax error here: missing closing parenthesis"
"@
$badCode | Set-Content -Path "test_syntax_error.py" -Encoding UTF8

git add test_syntax_error.py
Write-Host "`n=== 3. Спроба виконати git commit (повинно бути заблоковано) ===" -ForegroundColor Red
git commit -m "Attempt to commit invalid syntax"

Write-Host "`n=== 4. Очищення тимчасового тестового файлу ===" -ForegroundColor Green
git reset HEAD test_syntax_error.py
Remove-Item test_syntax_error.py -Force
Write-Host "Тест завершено. Pre-commit успішно заблокував коміт!" -ForegroundColor Cyan
