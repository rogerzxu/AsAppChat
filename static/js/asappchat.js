function addMessagesToChatHistory(messages) {
    $('#chatHistory').empty();
    for (i = 0 ; i < messages.length ; i++) {
        var message = messages[i];
        $('#chatHistory').append('<p>' +
            message.sender + ':&nbsp&nbsp&nbsp&nbsp&nbsp' +
            message.message_content + '</p>');
    }
}

$(document).ready(function() {
    $('.user').bind('click', function(e) {
        $('.user').removeAttr('style');
        e.preventDefault();
        $(this).css('color','#000000');
        var name = $(this).attr('name');
        $.ajax({
            type: "GET",
            url: "/chat-history/" + name,
            accepts: "application/json",
            success: function(data) {
                addMessagesToChatHistory(data.messages);
            }
        });
    });

    var socket = io.connect('http://' + document.domain + ':' + location.port + '/chat');
    socket.on('message', function(data) {
        $('#chatHistory').append('<p>NEW MESSAGE</p>');
    });

    $('#messageForm').on('submit', function(e) {
        e.preventDefault();
        var message = $('input[name=message]').val();
        socket.emit('text', {message: message})
    });
});
