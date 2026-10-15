<?php
// Run with `wp eval-file` against a disposable WordPress installation only.
if(!defined('ABSPATH')||!str_contains(home_url(),'openvist.test'))throw new Exception('Disposable test installation required');
function ovla_check($name,$condition){if(!$condition)throw new Exception('FAIL '.$name);echo 'PASS '.$name."\n";}
function ovla_request($method,$path,$body=[]){$r=new WP_REST_Request($method,'/openvist-link-auditor/v1/'.$path);$r->set_header('content-type','application/json');if($body)$r->set_body(wp_json_encode($body));return rest_do_request($r);}
do_action('rest_api_init');
$admin=get_user_by('login','testadmin')->ID;
$alice=wp_create_user('alice-test','fixture-only-password','alice@example.invalid');$bob=wp_create_user('bob-test','fixture-only-password','bob@example.invalid');
wp_set_current_user(0);ovla_check('Anonymous job access denied',ovla_request('GET','jobs')->get_status()===401);ovla_check('Anonymous worker access denied',ovla_request('POST','claim',['protocol'=>2])->get_status()===401);
wp_set_current_user($alice);ovla_check('Subscriber cannot claim jobs',ovla_request('POST','claim',['protocol'=>2])->get_status()===403);ovla_check('Paused service rejects public submission',ovla_request('POST','domains',['url'=>'https://example.com/'])->get_status()===503);
update_option('ovla_public_enabled','1');
foreach(['http://example.com/','https://127.0.0.1/','https://example.com/path','https://a..example.com/','https://user:pass@example.com/'] as $url)ovla_check('Invalid origin rejected '.$url,ovla_request('POST','domains',['url'=>$url])->get_status()===400);
$added=ovla_request('POST','domains',['url'=>'https://example.com/']);ovla_check('Domain stored',$added->get_status()===200);$domain=$added->get_data()['id'];
ovla_check('Unverified audit denied',ovla_request('POST','jobs',['domain_id'=>$domain])->get_status()===403);
$verification=ovla_request('POST','verify',['domain_id'=>$domain]);ovla_check('Verification queued',$verification->get_status()===200);
wp_set_current_user($bob);ovla_check('Other account cannot verify domain',ovla_request('POST','verify',['domain_id'=>$domain])->get_status()===404);ovla_check('Other account cannot remove domain',ovla_request('POST','remove-domain',['domain_id'=>$domain])->get_status()===404);ovla_check('Other account sees no jobs',ovla_request('GET','jobs')->get_data()['jobs']===[]);
wp_set_current_user($admin);ovla_check('Legacy worker cannot claim',ovla_request('POST','claim',[])->get_status()===409);
$claim=ovla_request('POST','claim',['protocol'=>2])->get_data();ovla_check('Worker receives verification proof',$claim['kind']==='verify'&&$claim['url']==='https://example.com/'&&strlen($claim['proof'])>64);ovla_check('Second claim cannot run concurrently',ovla_request('POST','claim',['protocol'=>2])->get_data()['state']==='busy');
$finish=['id'=>$claim['id'],'lease'=>$claim['lease'],'state'=>'completed','report'=>['verified'=>true]];ovla_check('Verification accepted',ovla_request('POST','finish',$finish)->get_status()===200);ovla_check('Delivery is idempotent',ovla_request('POST','finish',$finish)->get_status()===200);
wp_set_current_user($alice);ovla_check('Verified domain visible',ovla_request('GET','domains')->get_data()['domains'][0]['verified']===true);ovla_check('Verified audit queued',ovla_request('POST','jobs',['domain_id'=>$domain])->get_status()===200);
wp_set_current_user($admin);$claim=ovla_request('POST','claim',['protocol'=>2])->get_data();$report=['started_from'=>'https://example.com/','summary'=>['ok'=>1],'limits_reached'=>false,'results'=>[['url'=>'https://example.com/','status'=>200,'outcome'=>'ok']]];$finish=['id'=>$claim['id'],'lease'=>$claim['lease'],'state'=>'completed','report'=>$report];
$bad=$finish;$bad['report']['results'][0]['url']='https://elsewhere.example/';ovla_check('Foreign report URL rejected',ovla_request('POST','finish',$bad)->get_status()===400);
ovla_check('Audit delivered',ovla_request('POST','finish',$finish)->get_status()===200);
wp_set_current_user($alice);$rows=ovla_request('GET','jobs')->get_data()['jobs'];$audit_rows=array_values(array_filter($rows,static fn($r)=>$r['kind']==='audit'));ovla_check('Owner retrieves private result',$audit_rows[0]['report']===$report);ovla_check('Audit cooldown enforced',ovla_request('POST','jobs',['domain_id'=>$domain])->get_status()===429);
wp_set_current_user($bob);ovla_check('Private result not exposed to another account',ovla_request('GET','jobs')->get_data()['jobs']===[]);
wp_set_current_user($alice);ovla_check('Owner removes domain',ovla_request('POST','remove-domain',['domain_id'=>$domain])->get_status()===200);ovla_check('Domain removed',ovla_request('GET','domains')->get_data()['domains']===[]);foreach(ovla_request('GET','jobs')->get_data()['jobs'] as $row)ovla_check('Removed domain reports erased',$row['report']===null);
wp_set_current_user($admin);ovla_check('Late delivery discarded safely',ovla_request('POST','finish',$finish)->get_data()['discarded']===true);
global $wpdb;$t=OVLA_Bridge::table();$wpdb->insert($t,['id'=>str_repeat('f',32),'owner'=>$alice,'created'=>time()-86402,'state'=>'completed']);ovla_request('POST','claim',['protocol'=>2]);ovla_check('Expired jobs deleted',(int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM $t WHERE id=%s",str_repeat('f',32)))===0);
echo "WordPress database, REST permission, ownership, lease, privacy and retention checks passed.\n";
