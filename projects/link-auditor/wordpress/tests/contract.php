<?php
// Standalone contract harness. Does not exercise a live WordPress database.
error_reporting(E_ALL);
set_error_handler(static function($level,$message){throw new Exception($message);});
define('ABSPATH',__DIR__);
$GLOBALS['hooks']=[];$GLOBALS['admin']=false;$GLOBALS['pilot']='';$GLOBALS['routes']=[];
function add_action($hook,$callback,$priority=10,$args=1){$GLOBALS['hooks'][$hook][]=$callback;}
function add_filter($hook,$callback,$priority=10,$args=1){$GLOBALS['hooks'][$hook][]=$callback;}
function register_activation_hook($file,$callback){}
function register_deactivation_hook($file,$callback){}
function get_query_var($key){return $GLOBALS['pilot'];}
function current_user_can($cap){return in_array($cap,['read','manage_options'],true)&&$GLOBALS['admin'];}
function is_user_logged_in(){return $GLOBALS['admin'];}
function wp_json_encode($value){return json_encode($value);}
function register_rest_route($ns,$route,$args){$GLOBALS['routes'][]=$args;}
function check($name,$ok){if(!$ok)throw new Exception('FAIL '.$name);echo 'PASS '.$name."\n";}
require dirname(__DIR__).'/openvist-link-auditor-bridge.php';
check('Guest cannot access',!OVLA_Bridge::access());
$GLOBALS['admin']=true;check('Administrator can access',OVLA_Bridge::access());
OVLA_Bridge::routes();check('Nine authenticated routes registered',count($GLOBALS['routes'])===9);
foreach($GLOBALS['routes'] as $route){check('Route has explicit account or worker permission',in_array($route['permission_callback'],[[OVLA_Bridge::class,'access'],[OVLA_Bridge::class,'worker_access']],true));}
$report=['started_from'=>'https://openvist.com/','summary'=>['ok'=>1],'limits_reached'=>false,'results'=>[['url'=>'https://openvist.com/','status'=>200,'outcome'=>'ok']]];
check('Valid bounded report accepted',OVLA_Bridge::valid_report($report));
$bad=$report;$bad['summary']['ok']=2;check('False summary rejected',!OVLA_Bridge::valid_report($bad));
$bad=$report;$bad['results'][0]['url']='https://openvist.com.evil.example/';check('Foreign report origin rejected',!OVLA_Bridge::valid_report($bad));
$bad=$report;$bad['results'][0]['outcome']='invented';check('Unknown outcome rejected',!OVLA_Bridge::valid_report($bad));
$bad=$report;$bad['results'][0]['status']='200';check('Wrong status type rejected',!OVLA_Bridge::valid_report($bad));
$bad=$report;$bad['results']=array_fill(0,201,$report['results'][0]);check('Oversized result count rejected',!OVLA_Bridge::valid_report($bad));
echo "Contract checks passed. Live database and REST authentication still require verification.\n";
