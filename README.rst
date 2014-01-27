################
media-controller
################

Control a multi-elements media center, where the computer is not the central element

Configure the needed plugins in the configuration file, execute the controller,
and voilà!

Plugins
=======

Every input element and every controlled element is linked to a plugin. Plugins
communicate over a pseudo-bus and every ReceiverPlugin can take actions
depending on SenderPlugin messages.

Messages
========

The following standardized messages may be used:

sound:vol+ : increase the audio volume
sound:vol- : decrease the audio volume
sound:mute : mute the audio