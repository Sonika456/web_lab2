function fillFilmList() {
    fetch('/lab7/rest-api/films/')
    .then(function (data) {
        return data.json();
    })
    .then(function (films) {
        let tbody = document.getElementById('film-list');
        tbody.innerHTML = '';
        for(let i = 0; i<films.length; i++) {
            let tr = document.createElement('tr');

            let tdTitle = document.createElement('td'); 
            let tdTitleRus = document.createElement('td'); 
            let tdYear = document.createElement('td');
            let tdActions = document.createElement('td');

            tdTitleRus.innerText = films[i].title_ru;
            if (films[i].title && films[i].title != films[i].title_ru) {
                tdTitle.innerHTML = `(<i>${films[i].title}</i>)`; 
            } else {
                tdTitle.innerText = '';
            }
            tdYear.innerText = films[i].year;

            let editButton = document.createElement('button'); 
            editButton.innerText = 'Редактировать';
            editButton.onclick = function() {
                editFilm(i);
            };

            let delButton = document.createElement('button'); 
            delButton.innerText = 'Удалить';
            delButton.onclick = function() {
                deleteFilm(i, films[i].title_ru);
            };
            
            tdActions.append (editButton);
            tdActions.append (delButton);

            tr.append(tdTitleRus);
            tr.append(tdTitle);
            tr.append (tdYear);
            tr.append (tdActions);
            tbody.append(tr);
        }
    })
}
function deleteFilm(id, title) { 
    if(! confirm(`Вы точно хотите удалить фильм "${title}"?`))
        return;

    fetch(`/lab7/rest-api/films/${id}`, {method: 'DELETE'})
        .then(function () {
            fillFilmList();
        });
}
function showModal() {
    const errorElement = document.getElementById('description-error');
    if (errorElement) {
        errorElement.innerText = '';
    }
    document.querySelector('div.modal').style.display = 'block';
}
function hideModal() {
    document.querySelector('div.modal').style.display = 'none';
}
function cancel() {
    hideModal();
}
function addFilm() {
    document.getElementById('id').value =''; 
    document.getElementById('title').value =''; 
    document.getElementById('title-ru').value =''; 
    document.getElementById('year').value =''; 
    document.getElementById('description').value = '';
    showModal();
}
function sendFilm() {
    const id = document.getElementById('id').value;
    const film= {
        title: document.getElementById('title').value,
        title_ru: document.getElementById('title-ru').value, 
        year: document.getElementById('year').value, 
        description: document.getElementById('description').value
    }

    let url;
    let method;

    if (id === '') {
        url = `/lab7/rest-api/films/`; 
        method = 'POST';
    } else {
        url = `/lab7/rest-api/films/${id}`;
        method = 'PUT';
    }

    fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"}, 
        body: JSON.stringify(film)
    })
    .then(function(resp) { 
        if (resp.ok) {
            fillFilmList(); 
            hideModal();
            return{};
        }
        return resp.json();
    })
    .then(function(errors) {
        document.getElementById('title-ru-error').innerText = '';
        document.getElementById('title-error').innerText = '';
        document.getElementById('year-error').innerText = '';
        document.getElementById('description-error').innerText = '';

        if (errors.title_ru)
            document.getElementById('title-ru-error').innerText = errors.title_ru;
        if (errors.title)
            document.getElementById('title-error').innerText = errors.title;
        if (errors.year)
            document.getElementById('year-error').innerText = errors.year;
        if (errors.description)
            document.getElementById('description-error').innerText = errors.description;
    })
}
function editFilm(id) {
    fetch(`/lab7/rest-api/films/${id}`)
    .then(function (data) {
        return data.json();
    })
    .then(function (film) {
        document.getElementById('id').value = id;
        document.getElementById('title').value = film.title;
        document.getElementById('title-ru').value = film.title_ru;
        document.getElementById('year').value = film.year;
        document.getElementById('description').value = film.description; 
        showModal();
    });
}
