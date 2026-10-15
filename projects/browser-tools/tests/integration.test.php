<?php
// Minimal WordPress contract harness; not a replacement for live-site checks.
error_reporting(E_ALL);
set_error_handler(static function($level,$message){throw new Exception($message);});
define('ABSPATH',__DIR__);
$GLOBALS['hooks']=[];$GLOBALS['tool_route']='index';
function add_action($hook,$callback,$priority=10,$args=1){$GLOBALS['hooks'][$hook][]=$callback;}
function add_filter($hook,$callback,$priority=10,$args=1){$GLOBALS['hooks'][$hook][]=$callback;}
function register_activation_hook($file,$callback){}function register_deactivation_hook($file,$callback){}
function get_query_var($key,$default=''){return $key==='openvist_tool'?$GLOBALS['tool_route']:$default;}
function home_url($path='/'){return 'https://example.com'.$path;}
function esc_url($value){return htmlspecialchars($value,ENT_QUOTES,'UTF-8');}
function esc_html($value){return htmlspecialchars($value,ENT_QUOTES,'UTF-8');}
function esc_attr($value){return htmlspecialchars($value,ENT_QUOTES,'UTF-8');}
function get_header(){echo '<header>Shared header</header>';}
function get_footer(){echo '<footer>Shared footer</footer>';}
function status_header($status){$GLOBALS['status']=$status;}
function get_option($name){return $GLOBALS['blog_public']??'1';}
class WP_Sitemaps_Provider {public $name;public $object_type;}
function check($label,$ok){if(!$ok)throw new Exception($label);echo 'PASS '.$label."\n";}
require dirname(__DIR__).'/openvist-tools.php';
foreach(array_merge(['index'],array_keys(OpenViST_Tools::catalogue())) as $route){
    $GLOBALS['tool_route']=$route;
    ob_start();require dirname(__DIR__).'/template.php';$html=ob_get_clean();
    check('Renders route '.$route,str_contains($html,'ovt-shell')&&str_contains($html,'Shared footer'));
    check('No native form upload on '.$route,!str_contains($html,'<form'));
    ob_start();OpenViST_Tools::metadata();$meta=ob_get_clean();
    check('Tools canonical '.$route,str_contains($meta,OpenViST_Tools::url($route))&&substr_count($meta,'rel="canonical"')===1);
}
$GLOBALS['tool_route']='invalid';check('Unknown route ignored',OpenViST_Tools::route()==='');
$menu=$GLOBALS['hooks']['openvist_navigation_links'][0](['Directory'=>'/site/','Recipes'=>'/recipes/','Journal'=>'/journal/']);
check('Menu ordering',array_keys($menu)===['Directory','Recipes','Tools','Journal']);
$query=new class {public $is_home=true,$is_page=true,$is_singular=true,$is_archive=true,$is_404=true,$settings=[];function is_main_query(){return true;}function get($name){return 'csv-comparator';}function set($name,$value){$this->settings[$name]=$value;}};
$GLOBALS['hooks']['pre_get_posts'][0]($query);
check('Virtual route does not impersonate homepage',!$query->is_home&&!$query->is_singular&&$query->settings['post__in']===[0]);
$server=new stdClass();$server->registry=new class {public $provider;function add_provider($name,$provider){$candidate=false;foreach($GLOBALS['hooks']['wp_sitemaps_add_provider'] as $filter)$candidate=$filter($candidate,$name);$this->provider=$candidate;}};
$GLOBALS['hooks']['wp_sitemaps_init'][0]($server);
check('Tools sitemap survives conservative provider filter',count($server->registry->provider->get_url_list(1))===4);
$GLOBALS['blog_public']='0';
check('Private-site setting respected',$server->registry->provider->get_url_list(1)===[]&&$server->registry->provider->get_max_num_pages()===0);
echo "All integration contract checks passed.\n";
