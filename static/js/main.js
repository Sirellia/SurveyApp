function toggleOptions() {
    var t = document.getElementById('questionType').value;
    var c = document.getElementById('optionsContainer');
    var toggle = document.getElementById('correctAnswerToggle');

    if (t === 'single_choice' || t === 'multiple_choice') {
        c.style.display = 'block';
        toggle.style.display = 'block';
    } else if (t === 'yes_no') {
        c.style.display = 'none';
        toggle.style.display = 'block';
    } else {
        c.style.display = 'none';
        toggle.style.display = 'none';
    }

    document.getElementById('hasCorrectAnswer').checked = false;
    toggleCorrectAnswer();
}

function toggleCorrectAnswer() {
    var checked = document.getElementById('hasCorrectAnswer').checked;
    var t = document.getElementById('questionType').value;

    document.getElementById('correctSingleContainer').style.display = 'none';
    document.getElementById('correctMultipleContainer').style.display = 'none';
    document.getElementById('correctYesNoContainer').style.display = 'none';

    if (!checked) return;

    if (t === 'single_choice') {
        updateCorrectSingleOptions();
        document.getElementById('correctSingleContainer').style.display = 'block';
    } else if (t === 'multiple_choice') {
        updateCorrectMultipleOptions();
        document.getElementById('correctMultipleContainer').style.display = 'block';
    } else if (t === 'yes_no') {
        document.getElementById('correctYesNoContainer').style.display = 'block';
    }
}

function updateCorrectSingleOptions() {
    var options = document.querySelectorAll('#optionsList input[name="options[]"]');
    var select = document.getElementById('correctSingleSelect');
    select.innerHTML = '<option value="">-- Выберите правильный ответ --</option>';

    options.forEach(function (input) {
        if (input.value.trim()) {
            var opt = document.createElement('option');
            opt.value = input.value.trim();
            opt.textContent = input.value.trim();
            select.appendChild(opt);
        }
    });
}

function updateCorrectMultipleOptions() {
    var options = document.querySelectorAll('#optionsList input[name="options[]"]');
    var container = document.getElementById('correctMultipleList');
    container.innerHTML = '';

    options.forEach(function (input) {
        if (input.value.trim()) {
            var label = document.createElement('label');
            label.style.cssText = 'display:flex;align-items:center;gap:8px;padding:6px 0;cursor:pointer';
            label.innerHTML = '<input type="checkbox" name="correct_answers[]" value="' + input.value.trim() + '"> <span>' + input.value.trim() + '</span>';
            container.appendChild(label);
        }
    });
}

function addOption() {
    var l = document.getElementById('optionsList');
    var c = l.children.length + 1;
    var d = document.createElement('div');
    d.className = 'option-input';
    d.innerHTML = '<input type="text" name="options[]" placeholder="Вариант ' + c + '" oninput="onOptionChange()"><button type="button" class="btn-icon btn-delete" onclick="removeOption(this)">×</button>';
    l.appendChild(d);
}

function removeOption(b) {
    var l = document.getElementById('optionsList');
    if (l.children.length > 2) {
        b.parentElement.remove();
        onOptionChange();
    } else {
        alert('Минимум 2 варианта ответа');
    }
}

function onOptionChange() {
    if (document.getElementById('hasCorrectAnswer').checked) {
        var t = document.getElementById('questionType').value;
        if (t === 'single_choice') updateCorrectSingleOptions();
        if (t === 'multiple_choice') updateCorrectMultipleOptions();
    }
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('#optionsList input[name="options[]"]').forEach(function (input) {
        input.addEventListener('input', onOptionChange);
    });
});

function copyLink(link) {
    navigator.clipboard.writeText(link).then(function () {
        var n = document.createElement('div');
        n.className = 'alert alert-success';
        n.innerHTML = 'Ссылка скопирована! <button class="alert-close" onclick="this.parentElement.remove()">×</button>';
        var m = document.querySelector('main.container');
        m.insertBefore(n, m.firstChild);
        setTimeout(function () { n.remove(); }, 3000);
    }).catch(function () { prompt('Скопируйте ссылку:', link); });
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.alert').forEach(function (a) {
        setTimeout(function () { a.style.opacity = '0'; a.style.transition = 'opacity 0.5s'; setTimeout(function () { a.remove(); }, 500); }, 5000);
    });
});