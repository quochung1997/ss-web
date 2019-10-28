
$('#txt').keypress(function (e) {
  if (e.which == 13) {
    handleRequest();
  }
});

const handleRequest = () => {
    const val = $('#txt').val();
    const a = {
        data: val
    };

    console.log(a);

    $.ajax({
        url: 'api',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            $('#out').html(data.data);
        },
        data: JSON.stringify(a)
    });
}

$('#btn').click(handleRequest);
