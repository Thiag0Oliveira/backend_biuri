$('#form-signup-executive').submit(function(ev) {
    var element = document.getElementById("erro");
    ev.preventDefault();
    const form = $(this);    
    $.ajax({
        type: form.attr('method'),
        url: form.attr('action'),
        data: form.serialize(),
        success: function(data){
            $('#executive-id').val(data.id);
            $('#id_modal-name').val(data.name);
            $('#id_modal-cpf').val(data.cpf);
            $('#id_modal-email').val(data.email);
            $('#id_modal-telephone').val(data.telephone);
            $("#signupModal").modal('show');
            console.log('success',data.name);
        },
        error: function(data){
            data = data.responseJSON
            element.innerHTML = `${data.message}`;
        }
    });
    
});

$('#form-signup-executive-modal').submit(function(ev) {
    ev.preventDefault();
    const form = $(this);
    $.ajax({
        type: form.attr('method'),
        url: form.attr('action'),
        data: form.serialize() + '&executive-id=' + $('#executive-id').val(),
        success: function(data){
            console.log('success',data);
            $("#signupModal").modal('toggle');
            swal({title: 'Cadastro realizado com Sucesso!',
                text: 'Em breve entraremos em contato com você.',
                showConfirmButton: false,
                timer: 3000,
                type: 'success'});
        },
        error: function(data){
            data = data.responseJSON
            alert(`${data.message}`);
        }
    });
    
});

$('#form-signup-profissional').submit(function(ev) {
    var element = document.getElementById("erro");
    ev.preventDefault();
    const form = $(this);
    $.ajax({
        type: form.attr('method'),
        url: form.attr('action'),
        data: form.serialize(),
        success: function(data){
            form[0].reset();
            $('#id_category').val(null).trigger('change');
            swal({title: 'Cadastro realizado com Sucesso!',
                text: 'Em breve entraremos em contato com você.',
                showConfirmButton: false,
                timer: 3000,
                type: 'success'});
            console.log('success',data.name);
        },
        error: function(data){
            data = data.responseJSON
            element.innerHTML = `${data.message}`;
        }
    });
    
});

$('#form-signup-profissional-modal').submit(function(ev) {
    ev.preventDefault();
    const form = $(this);
    $.ajax({
        type: form.attr('method'),
        url: form.attr('action'),
        data: form.serialize() + '&profissional-id=' + $('#profissional-id').val(),
        success: function(data){
            console.log('success',data);
            $("#signupModal").modal('toggle');
            swal({title: 'Cadastro realizado com Sucesso!',
                text: 'Em breve entraremos em contato com você.',
                showConfirmButton: false,
                timer: 3000,
                type: 'success'});
        },
        error: function(data){
            data = data.responseJSON
            alert(`${data.message}`);
        }
    });
    
});

$(function(){
    $('.select2.categoria').select2({
        placeholder: 'Categoria'
      });
})