selected_user = null;

const toggle_username_input = () => {
	if($('#username_input_id').is(':visible')) {
		$('#username_input_id').hide();
	}
	else {
		$('#username_input_id').show();
	}
}
const add_user_message = (message) => {
	$('#user_chat_box').append(`<div class='message bg-light'><span><b>${message.author}</b> ${message.date}</sapn> <p>${message.content}</p></div>`);
	$('#user_chat_box').scrollTop(10000);

}
const set_user_chat_title = (title) => {
	$('#chat_title').html(title);
}
const clear_chat = () => {
	$('#user_chat_box').html('');
}
$(document).on('submit', '#username_input_id', function(event) {
	event.preventDefault();
	$.ajax({url:'/add-contact', type:'POST', data: {'username': $('#username_input').val()}}).done(function(data) {
		if(data.error) {
			console.log(data.error);
		}
		else {
			$('#menulist').append(`<div><a class="w3-bar-item w3-button user" id='*${data.id}' style='text-decoration:none'><img width=35 class="user-avatar" src="${data.img_url}"> ${data.name}</a></div>`);
		}
	});
	$('#username_input').val('');
});
$(document).on('click', '.user', function() {
	id = parseInt($(this).attr('id').slice(1, $(this).attr('id').length), 10);
	selected_user = id;
	this_element = $(this);
	$.ajax({url:`retrieve-directmessages/${id}`, type:'POST'}).done(function(data) {
		console.log(data);
		clear_chat();
		set_user_chat_title(this_element.html());
		for(let i = 0; i < data.messages.length; i++) {
			add_user_message(data.messages[i]);
		}
	});
});
$(document).on('submit', '#message_input', function(e) {
	e.preventDefault();
	message = $('#message_input input').val()
	if (selected_user && message) {
		socket.emit('direct_message', {'to': selected_user, 'message': message});
	}
	$(this).children('input').val('');
});
socket.on('direct_message', function(data) {
	add_user_message(data);
});