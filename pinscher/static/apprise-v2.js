// Global Apprise variables
var $Apprise = null,
		$overlay = null,
		$body = null,
		$window = null,
		$cA = null,
		AppriseQueue = [];

// Add overlay and set opacity for cross-browser compatibility
$(function() {
	$Apprise = $('<div class="apprise">');
	$overlay = $('<div class="apprise-overlay">');
	$body = $('body');
	$window = $(window);
	$body.append($overlay).append($Apprise);
});
function Apprise(text, options) {
	if(text===undefined || !text) {
		return false;
	}
	var $me = this,
		$_inner = $('<div class="apprise-inner">'),
		$_buttons = $('<div class="apprise-buttons">'),
		$_input = $('<input type="password">');
	var settings = {	
		animation: 700,	// Animation speed
		buttons: {
			confirm: {
				action: function() { $me.disappear(); }, // Callback function
				className: null, // Custom class name(s)
				id: 'confirm', // Element ID
				text: 'Ok' // Button text
			}
		},
		input: false, // input dialog
		override: true // Override browser navigation while Apprise is visible
	};
	$.extend(settings, options);
	if(text=='close') { 
		$cA.disappear();
		return;
	}
	if($Apprise.is(':visible')) {
		AppriseQueue.push({text: text, options: settings});
		return;
	}
	this.disappear = function() {
		$Apprise.animate({
			top: '-100%'
		}, settings.animation, function() {
			$overlay.fadeOut(200);
			$Apprise.hide();
			$window.unbind("beforeunload");
			$window.unbind("keydown");
			if(AppriseQueue[0]) { 
				Apprise(AppriseQueue[0].text, AppriseQueue[0].options);
				AppriseQueue.splice(0,1);
			}
		});
		return;
	};
	this.keyPress = function() {
		$window.bind('keydown', function(e) {
			if(e.keyCode===27) {
				if(settings.buttons.cancel) {
					$("#apprise-btn-" + settings.buttons.cancel.id).trigger('click');
				} else {
					$me.disappear();
				}
			} else if(e.keyCode===13) {
				if(settings.buttons.confirm) {
					$("#apprise-btn-" + settings.buttons.confirm.id).trigger('click');
				} else {
					$me.disappear();
				}
			}
		});
	};
	$.each(settings.buttons, function(i, button) {
		if(button) {
			var $_button = $('<button id="apprise-btn-' + button.id + '">').append(button.text);
			if(button.className) {
				$_button.addClass(button.className);
			}
			$_buttons.append($_button);
			$_button.on("click", function() {
				var response = {
					clicked: button, // Pass back the object of the button that was clicked
					input: ($_input.val() ? $_input.val() : null) // User inputted text
				};
				button.action( response );
			});
		}
	});
	if(settings.override) {
		$window.bind('beforeunload', function(e){ 
			return "An alert requires attention";
		});
	}
	$Apprise.html('').append( $_inner.append('<div class="apprise-content">' + text + '</div>') ).append($_buttons);
	$cA = this;
	if(settings.input) {
		$_inner.find('.apprise-content').append( $('<div class="apprise-input">').append( $_input ) );
	}
	$overlay.fadeIn(300);
	$Apprise.show().animate({
		top: '20%'
	}, 
		settings.animation, 
		function() {
			$me.keyPress();
		}
	);
	if(settings.input) {
		$_input.focus();
	}
}
