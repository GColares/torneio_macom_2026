import glob

for f in glob.glob('templates/*.html'):
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Only update files that have the relatorios link in the sidebar but don't have credenciamento yet
        if 'url \'relatorios\'' in content and 'sidebar-nav' in content and 'url \'credenciamento\'' not in content:
            new_content = content.replace(
                '<a href="{% url \'relatorios\' %}"><i class="fa-solid fa-print"></i> Relatórios</a>',
                '<a href="{% url \'relatorios\' %}"><i class="fa-solid fa-print"></i> Relatórios</a>\n            <a href="{% url \'credenciamento\' %}"><i class="fa-solid fa-id-badge"></i> Credenciamento</a>'
            )
            # Also handle if relatorios has class="active"
            new_content = new_content.replace(
                '<a href="{% url \'relatorios\' %}" class="active"><i class="fa-solid fa-print"></i> Relatórios</a>',
                '<a href="{% url \'relatorios\' %}" class="active"><i class="fa-solid fa-print"></i> Relatórios</a>\n            <a href="{% url \'credenciamento\' %}"><i class="fa-solid fa-id-badge"></i> Credenciamento</a>'
            )
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"Updated {f}")
    except Exception as e:
        print(f"Error on {f}: {e}")
