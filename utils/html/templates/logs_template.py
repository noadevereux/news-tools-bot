import jinja2

logs_template = jinja2.Template(
    """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-4bw+/aepP/YC94hEpVNVgiZdgIC5+VKNBQNGCHeKRQN+PtmoHDEXuppvnDJzQIu9" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/js/bootstrap.bundle.min.js" integrity="sha384-HwwvtgBNo3bZJJLYd8oVXjrBZt8cqVSpeBNS5n7C8IVInixGAoxmnlMuBnhbgrkm" crossorigin="anonymous"></script>
    <title>{{ title }}</title>
</head>
<body>
    <div class="container">
        <div class="mt-5">
            <h2 class="text-center">{{ title }}</h2>
            <div class="mt-4">
                <table class="table table-striped table-secondary table-hover">
                    <thead>
                      <tr>
                        <th scope="col">ID действия</th>
                        <th scope="col">Действие</th>
                        <th scope="col">Дата и время</th>
                      </tr>
                    </thead>
                    <tbody>
                      {% for action in actions -%}
                      <tr>
                        <th scope="row">{{ action[0] }}</th>
                        <td>{{ action[1] }}</td>
                        <td>{{ action[2] }}</td>
                      </tr>
                      {%- endfor -%}
                    </tbody>
                  </table>
            </div>
        </div>
        <div class="mt-5 mb-5 text-center">
            <p class="text-center fw-lighter opacity-75 lh-1">
                © News Tools | Arizona Scottdale<br>
                An open-source tool for news department
            </p>
            <svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi bi-github" viewBox="0 0 16 16">
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            <a href="https://github.com/inlovewithxanny/news-tools" target="_blank" class="btn btn-outline-dark btn-sm">Github</a>
        </div>
    </div>
</body>
</html>"""
)
