# Налаштування та демонстрація роботи Pre-commit хуків (ЛР №1)

## 1. Призначення Pre-commit хуків
Pre-commit — це інструмент автоматизації перевірки коду перед збереженням змін у системі контролю версій Git.
Він гарантує, що:
- Жоден розробник не зможе зафіксувати коміт із синтаксичними помилками (`SyntaxError`).
- Код відповідає єдиному стандарту форматування (PEP 8) та правилам лінтера Ruff.
- Відсутні зайві пробіли в кінці рядків (`trailing-whitespace`) та пошкоджені YAML-файли конфігурації (`check-yaml`).

---

## 2. Конфігурація `.pre-commit-config.yaml`
У корені проєкту розміщено конфігураційний файл:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.10
    hooks:
      - id: ruff
        args: [ --fix ]
      - id: ruff-format
```

---

## 3. Встановлення та активація хуків
Для прив'язки хуків до локального Git-репозиторію виконайте:
```bash
# Встановлення pre-commit хука в .git/hooks/pre-commit
pre-commit install
```
Після цієї команди Git автоматично запускатиме всі перевірки при кожній спробі виконати `git commit`.

---

## 4. Сценарій демонстрації роботи для викладача (2 бали)

### Крок 1: Спроба закомітити код із синтаксичною або стилістичною помилкою
Створимо тимчасовий файл або внесемо навмисну помилку (наприклад, незакрита дужка або невідформатований код):
```python
# test_broken.py
def broken_syntax(
    x = 1
    return x
```
Додаємо файл до індексу Git і пробуємо виконати коміт:
```bash
git add test_broken.py
git commit -m "Test commit with broken code"
```

### Результат: Система автоматично блокує коміт!
```text
check yaml...........................................(no files to check)Skipped
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
ruff.....................................................................Failed
- hook id: ruff
- exit code: 1

test_broken.py:3:5: E999 SyntaxError: invalid syntax

ruff-format..............................................................Failed
- hook id: ruff-format
- exit code: 1

Error: Failed to parse test_broken.py:3:5: invalid syntax
```
> **Висновок**: Git скасовує створення коміту (`Commit aborted`), запобігаючи потраплянню зламаного коду у репозиторій.

---

### Крок 2: Виправлення помилки та успішне створення коміту
Виправляємо синтаксис та запускаємо перевірку:
```bash
# Ручний запуск усіх хуків на всіх файлах проєкту:
pre-commit run --all-files
```
Виведення:
```text
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
```
Тепер коміт створюється безперешкодно:
```bash
git commit -m "Clean code passes all pre-commit hooks"
# [master a1b2c3d] Clean code passes all pre-commit hooks
```
