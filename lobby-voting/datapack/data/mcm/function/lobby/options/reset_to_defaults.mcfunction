data remove storage mcm:options options

data merge storage mcm:options {init:1}

function mcm:lobby/options/summon_options
function mcm:extensions/options/init

data remove storage mcm:options init
function mcm:lobby/voting/enabled_changed
