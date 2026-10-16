<?php
/**
 * Plugin Name: OpenViST Link Auditor Bridge
 * Description: Account-based link audits for verified domains, processed by the OpenViST VPS.
 * Version: 0.2.5
 * Requires at least: 6.5
 * Requires PHP: 8.0
 * License: GPL-2.0-or-later
 */
defined('ABSPATH')||exit;
final class OVLA_Bridge {
    const VERSION='0.2.5';
    const NS='openvist-link-auditor/v1';
    public static function table(){global $wpdb;return $wpdb->prefix.'ovla_jobs';}
    public static function domains_table(){global $wpdb;return $wpdb->prefix.'ovla_domains';}
    public static function install(){
        global $wpdb;require_once ABSPATH.'wp-admin/includes/upgrade.php';
        $table=self::table();$domains=self::domains_table();$charset=$wpdb->get_charset_collate();
        dbDelta("CREATE TABLE $table (
            id varchar(32) NOT NULL,
            owner bigint(20) unsigned NOT NULL,
            created bigint(20) unsigned NOT NULL,
            started bigint(20) unsigned NOT NULL DEFAULT 0,
            state varchar(20) NOT NULL,
            lease varchar(64) NOT NULL DEFAULT '',
            report longtext NULL,
            kind varchar(12) NOT NULL DEFAULT 'audit',
            target varchar(300) NOT NULL DEFAULT 'https://openvist.com/',
            domain_id varchar(64) NOT NULL DEFAULT '',
            PRIMARY KEY  (id),
            KEY state_created (state,created),
            KEY owner_created (owner,created)
        ) $charset;");
        dbDelta("CREATE TABLE $domains (
            id varchar(64) NOT NULL,
            owner bigint(20) unsigned NOT NULL,
            target varchar(300) NOT NULL,
            token varchar(64) NOT NULL,
            created bigint(20) unsigned NOT NULL,
            verified bigint(20) unsigned NOT NULL DEFAULT 0,
            PRIMARY KEY  (id),
            KEY owner_created (owner,created)
        ) $charset;");
        update_option('ovla_schema_version',self::VERSION,false);
        self::rules();flush_rewrite_rules(false);
    }
    public static function route(){return (string)get_query_var('ovla_pilot')==='1';}
    public static function rules(){add_rewrite_rule('^tools/link-auditor/?$','index.php?ovla_pilot=1','top');}
    public static function worker_access(){return current_user_can('manage_options');}
    public static function access(){return is_user_logged_in()&&current_user_can('read');}
    public static function enabled(){return get_option('ovla_public_enabled')==='1';}
    public static function url(){return home_url('/tools/link-auditor/');}
    public static function origin($url){
        if(!is_string($url)||strlen($url)>265||!preg_match('~^https://([a-z0-9](?:[a-z0-9.-]*[a-z0-9])?)/?$~D', $url,$m))return false;
        $host=$m[1];if(strlen($host)>253||!str_contains($host,'.')||filter_var($host,FILTER_VALIDATE_IP))return false;
        foreach(explode('.',$host) as $label){if(!preg_match('/^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/D',$label))return false;}
        return 'https://'.$host.'/';
    }
    public static function local_admin($target){return $target==='https://openvist.com/'&&self::worker_access();}
    public static function boot(){
        add_action('init',[__CLASS__,'rules']);
        add_action('init',static function(){if(self::worker_access()&&get_option('ovla_schema_version')!==self::VERSION)self::install();},20);
        add_filter('query_vars',static function($v){$v[]='ovla_pilot';return $v;});
        add_action('pre_get_posts',static function($q){if(!$q->is_main_query()||(string)$q->get('ovla_pilot')!=='1')return;$q->is_home=false;$q->is_page=false;$q->is_singular=false;$q->is_archive=false;$q->is_404=false;$q->set('post__in',[0]);$q->set('no_found_rows',true);},100);
        add_action('template_redirect',static function(){if(self::route()){nocache_headers();status_header(200);global $wp_query;$wp_query->is_404=false;remove_action('wp_head','rel_canonical');}});
        add_filter('redirect_canonical',static function($url){return self::route()?false:$url;});
        add_filter('template_include',static function($t){return self::route()?__DIR__.'/template.php':$t;},PHP_INT_MAX);
        add_filter('body_class',static function($c){if(self::route())$c=array_merge($c,['openvist-public-ui','ovt-page']);return array_unique($c);});
        add_filter('pre_get_document_title',static function($t){return self::route()?'Link Auditor — Check links on your website | OpenViST':$t;},999);
        add_filter('openvist_brand_metadata_enabled',static function($on){return self::route()?false:$on;});
        add_action('wp_head',static function(){if(!self::route())return;echo '<link rel="canonical" href="'.esc_url(self::url()).'">' . "\n";echo '<meta name="description" content="Check HTTP links on a verified website. Free bounded audits with private results, clear limits and open-source code.">' . "\n";echo '<meta property="og:title" content="OpenViST Link Auditor"><meta property="og:description" content="Check links on a verified website with a free, bounded audit."><meta property="og:url" content="'.esc_url(self::url()).'"><meta property="og:type" content="website"><meta name="twitter:card" content="summary">';},2);
        add_action('wp_head',static function(){
            if(!self::route())return;
            $asset='openvist-directory-ui/assets/brand/openvist-logo-square-512x512.png';
            $image=file_exists(WP_PLUGIN_DIR.'/'.$asset)?plugins_url($asset):get_site_icon_url(512);
            if($image)echo '<meta property="og:image" content="'.esc_url($image).'"><meta property="og:image:alt" content="OpenViST logo"><meta name="twitter:image" content="'.esc_url($image).'">';
        },3);
        add_action('admin_menu',static function(){add_management_page('OpenViST Link Auditor','Link Auditor','manage_options','ovla-pilot',[__CLASS__,'admin_page']);});
        add_action('admin_post_ovla_toggle',static function(){if(!self::worker_access())wp_die('Not allowed.');check_admin_referer('ovla_toggle');$on=isset($_POST['enabled'])&&$_POST['enabled']==='1';if($on&&(int)get_option('ovla_worker_seen',0)<time()-600)wp_die('Run the 0.4.0 VPS worker within the last ten minutes first.');update_option('ovla_public_enabled',$on?'1':'0',false);wp_safe_redirect(admin_url('tools.php?page=ovla-pilot'));exit;});
        add_action('wp_enqueue_scripts',static function(){
            if(class_exists('OpenViST_Tools')&&OpenViST_Tools::route()==='index'){wp_enqueue_script('ovla-entry',plugins_url('assets/entry.js',__FILE__),[],self::VERSION,true);wp_add_inline_script('ovla-entry','window.ovlaEntry='.wp_json_encode(self::url()).';','before');}
            if(!self::route())return;
            wp_enqueue_style('ovla-pilot',plugins_url('assets/pilot.css',__FILE__),[],self::VERSION);
            wp_enqueue_script('ovla-copy-code',plugins_url('assets/copy-code.js',__FILE__),[],self::VERSION,true);
            if(self::access()){wp_enqueue_script('ovla-pilot',plugins_url('assets/pilot.js',__FILE__),[],self::VERSION,true);wp_add_inline_script('ovla-pilot','window.ovlaConfig='.wp_json_encode(['api'=>rest_url(self::NS),'nonce'=>wp_create_nonce('wp_rest')]).';','before');}
        });
        add_action('rest_api_init',[__CLASS__,'routes']);
        add_action('wp_sitemaps_init',static function($server){if(!class_exists('WP_Sitemaps_Provider'))return;$provider=new class extends WP_Sitemaps_Provider {
            public function __construct(){$this->name='openvist-link-auditor';$this->object_type='openvist-link-auditor';}
            public function get_url_list($page_num,$object_subtype=''){return (int)$page_num===1&&(string)get_option('blog_public')==='1'?[['loc'=>OVLA_Bridge::url()]]:[];}
            public function get_max_num_pages($object_subtype=''){return (string)get_option('blog_public')==='1'?1:0;}
        };add_filter('wp_sitemaps_add_provider',static function($p,$name)use($provider){return $name==='openvist-link-auditor'?$provider:$p;},120,2);$server->registry->add_provider('openvist-link-auditor',$provider);});
    }
    public static function admin_page(){
        echo '<div class="wrap"><h1>OpenViST Link Auditor</h1><p>Public submissions: '.(self::enabled()?'enabled':'paused').'. A compatible worker must have polled within the last ten minutes before enabling.</p><form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field('ovla_toggle');echo '<input type="hidden" name="action" value="ovla_toggle"><label><input type="checkbox" name="enabled" value="1" '.checked(self::enabled(),true,false).'> Enable verified-domain submissions for signed-in users</label><p>';submit_button('Save availability','primary','submit',false);echo '</p></form><a href="'.esc_url(self::url()).'">Open Link Auditor</a></div>';
    }
    public static function routes(){
        foreach(['/jobs'=>['GET'=>'listing','POST'=>'submit'],'/domains'=>['GET'=>'domains','POST'=>'add_domain'],'/verify'=>['POST'=>'verify'],'/remove-domain'=>['POST'=>'remove_domain']] as $path=>$methods){foreach($methods as $m=>$cb)register_rest_route(self::NS,$path,['methods'=>$m,'callback'=>[__CLASS__,$cb],'permission_callback'=>[__CLASS__,'access']]);}
        foreach(['/health'=>'health','/claim'=>'claim','/finish'=>'finish'] as $path=>$cb)register_rest_route(self::NS,$path,['methods'=>$path==='/health'?'GET':'POST','callback'=>[__CLASS__,$cb],'permission_callback'=>[__CLASS__,'worker_access']]);
    }
    private static function locked($callback){
        global $wpdb;$name='ovla_'.md5(DB_NAME.self::table());if((string)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s,0)',$name))!=='1')return new WP_Error('busy','Queue busy. Try again shortly.',['status'=>429]);
        try{$t=self::table();$d=self::domains_table();$now=time();$wpdb->query($wpdb->prepare("UPDATE $t SET state='interrupted' WHERE state='running' AND started<%d",$now-300));$wpdb->query($wpdb->prepare("DELETE FROM $t WHERE created<%d",$now-86400));$wpdb->query($wpdb->prepare("DELETE FROM $d WHERE (verified=0 AND created<%d) OR (verified>0 AND verified<%d)",$now-86400,$now-604800));return $callback();}finally{$wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)',$name));}
    }
    private static function availability(){return !self::enabled()&&!self::worker_access()?new WP_Error('paused','Submissions are temporarily paused.',['status'=>503]):null;}
    private static function owned($id){global $wpdb;if(!is_string($id)||!preg_match('/^[a-f0-9]{64}$/D',$id))return null;$d=self::domains_table();return $wpdb->get_row($wpdb->prepare("SELECT * FROM $d WHERE id=%s AND owner=%d",$id,get_current_user_id()),ARRAY_A);}
    public static function domains(){
        global $wpdb;$d=self::domains_table();$rows=$wpdb->get_results($wpdb->prepare("SELECT id,target,token,created,verified FROM $d WHERE owner=%d AND created>%d ORDER BY created DESC LIMIT 3",get_current_user_id(),time()-604800),ARRAY_A);
        foreach($rows as &$r){$r['verified']=(int)$r['verified']>time()-604800;$r['proof_url']=rtrim($r['target'],'/').'/.well-known/openvist-audit.txt';$r['proof_text']='openvist-audit-verification='.$r['token'];unset($r['token']);}
        $response=new WP_REST_Response(['domains'=>$rows,'enabled'=>self::enabled()||self::worker_access()],200);$response->header('Cache-Control','no-store, private');return $response;
    }
    public static function add_domain($request){return self::locked(static function()use($request){
        if($error=self::availability())return $error;global $wpdb;$d=self::domains_table();$owner=get_current_user_id();$target=self::origin($request->get_param('url'));if(!$target)return new WP_Error('domain','Enter an HTTPS website origin such as https://example.com/. Use an ASCII or punycode hostname, without a path, port, query or IP address.',['status'=>400]);
        $id=hash('sha256',$owner.'|'.$target);$old=self::owned($id);if($old)return ['id'=>$id];
        if((int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM $d WHERE owner=%d",$owner))>=3||(int)$wpdb->get_var("SELECT COUNT(*) FROM $d")>=1000)return new WP_Error('capacity','Domain capacity reached. Remove an unused domain or try later.',['status'=>429]);
        $now=time();$row=['id'=>$id,'owner'=>$owner,'target'=>$target,'token'=>bin2hex(random_bytes(32)),'created'=>$now,'verified'=>self::local_admin($target)?$now:0];
        if(!$wpdb->insert($d,$row))return new WP_Error('storage','Could not save domain.',['status'=>500]);return ['id'=>$id];
    });}
    private static function enqueue($domain,$kind){
        global $wpdb;$t=self::table();$owner=get_current_user_id();$now=time();$day=$now-86400;
        if((int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM $t WHERE owner=%d AND state IN ('queued','running')",$owner)))return new WP_Error('pending','Wait for your current job to finish.',['status'=>429]);
        if((int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM $t WHERE owner=%d AND kind=%s AND created>%d",$owner,$kind,$day))>=3)return new WP_Error('quota','Limit: three audits and three verification attempts per account in a rolling 24 hours.',['status'=>429]);
        if($kind==='audit'&&(int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM $t WHERE domain_id=%s AND kind='audit' AND created>%d",$domain['id'],$now-900)))return new WP_Error('cooldown','Wait 15 minutes between audits of this domain.',['status'=>429]);
        $global=$kind==='audit'?30:50;if((int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM $t WHERE kind=%s AND created>%d",$kind,$day))>=$global||(int)$wpdb->get_var("SELECT COUNT(*) FROM $t WHERE state IN ('queued','running')")>=10)return new WP_Error('full','Service capacity reached. Please try later.',['status'=>429]);
        $id=bin2hex(random_bytes(16));if(!$wpdb->insert($t,['id'=>$id,'owner'=>$owner,'created'=>$now,'state'=>'queued','kind'=>$kind,'target'=>$domain['target'],'domain_id'=>$domain['id']]))return new WP_Error('storage','Could not store job.',['status'=>500]);return ['id'=>$id,'state'=>'queued'];
    }
    public static function verify($request){return self::locked(static function()use($request){if($error=self::availability())return $error;$d=self::owned($request->get_param('domain_id'));if(!$d)return new WP_Error('domain','Domain not found.',['status'=>404]);return self::enqueue($d,'verify');});}
    public static function submit($request){return self::locked(static function()use($request){if($error=self::availability())return $error;$d=self::owned($request->get_param('domain_id'));if(!$d||(int)$d['verified']<=time()-604800)return new WP_Error('verification','Verify domain ownership before requesting an audit.',['status'=>403]);return self::enqueue($d,'audit');});}
    public static function remove_domain($request){return self::locked(static function()use($request){global $wpdb;$d=self::owned($request->get_param('domain_id'));if(!$d)return new WP_Error('domain','Domain not found.',['status'=>404]);$t=self::table();$wpdb->update($t,['state'=>'cancelled','report'=>null],['domain_id'=>$d['id'],'owner'=>get_current_user_id()]);$wpdb->delete(self::domains_table(),['id'=>$d['id'],'owner'=>get_current_user_id()]);return ['removed'=>true];});}
    public static function claim($request){
        if($request->get_param('protocol')!==2)return new WP_Error('protocol','Upgrade the VPS worker to protocol 2.',['status'=>409]);
        update_option('ovla_worker_seen',time(),false);
        return self::locked(static function(){global $wpdb;$t=self::table();if((int)$wpdb->get_var("SELECT COUNT(*) FROM $t WHERE state='running'")>0)return ['state'=>'busy'];$row=$wpdb->get_row("SELECT * FROM $t WHERE state='queued' ORDER BY created,id LIMIT 1",ARRAY_A);if(!$row)return ['state'=>'idle'];$d=self::domains_table();$domain=$wpdb->get_row($wpdb->prepare("SELECT * FROM $d WHERE id=%s AND owner=%d",$row['domain_id'],$row['owner']),ARRAY_A);if(!$domain){$wpdb->update($t,['state'=>'cancelled'],['id'=>$row['id']]);return ['state'=>'idle'];}
            $trusted=$row['target']==='https://openvist.com/'&&user_can((int)$row['owner'],'manage_options');
            if($row['kind']==='audit'&&(int)$domain['verified']<=time()-604800){$wpdb->update($t,['state'=>'cancelled'],['id'=>$row['id']]);return ['state'=>'idle'];}
            $lease=bin2hex(random_bytes(32));if($wpdb->update($t,['state'=>'running','started'=>time(),'lease'=>hash('sha256',$lease)],['id'=>$row['id'],'state'=>'queued'])!==1)return new WP_Error('claim','Could not claim job.',['status'=>409]);
            return ['state'=>'running','protocol'=>2,'kind'=>$row['kind'],'id'=>$row['id'],'lease'=>$lease,'url'=>$row['target'],'proof'=>'openvist-audit-verification='.$domain['token'],'trusted_local'=>$trusted];
        });
    }
    public static function valid_report($report,$target='https://openvist.com/'){
        if(!is_array($report)||($report['started_from']??'')!==$target||!isset($report['summary'],$report['results'],$report['limits_reached'])||!is_array($report['summary'])||!is_array($report['results'])||count($report['results'])>200||!is_bool($report['limits_reached']))return false;
        $allowed=['ok','missing','restricted','rate_limited','server_error','http_error','request_error','robots_denied','robots_unavailable','external_redirect_not_checked','not_checked'];$counts=[];
        foreach($report['results'] as $r){if(!is_array($r)||!in_array($r['outcome']??'',$allowed,true)||!is_string($r['url']??null)||strlen($r['url'])>4096||!str_starts_with($r['url'],$target)||!array_key_exists('status',$r)||($r['status']!==null&&(!is_int($r['status'])||$r['status']<100||$r['status']>599)))return false;$counts[$r['outcome']]=($counts[$r['outcome']]??0)+1;}
        ksort($counts);$summary=$report['summary'];ksort($summary);return $counts===$summary&&strlen(wp_json_encode($report))<=2097152;
    }
    public static function finish($request){
        if(strlen($request->get_body())>2200000)return new WP_Error('size','Report too large.',['status'=>413]);$id=$request->get_param('id');$lease=$request->get_param('lease');$state=$request->get_param('state');$report=$request->get_param('report');
        if(!is_string($id)||!preg_match('/^[a-f0-9]{32}$/D',$id)||!is_string($lease)||!preg_match('/^[a-f0-9]{64}$/D',$lease)||!in_array($state,['completed','failed','timed_out'],true))return new WP_Error('invalid','Invalid result.',['status'=>400]);
        return self::locked(static function()use($id,$lease,$state,$report){global $wpdb;$t=self::table();$old=$wpdb->get_row($wpdb->prepare("SELECT * FROM $t WHERE id=%s",$id),ARRAY_A);if(!$old)return new WP_Error('expired','Job expired.',['status'=>410]);if(!$old['lease']||!hash_equals($old['lease'],hash('sha256',$lease)))return new WP_Error('lease','Result lease no longer active.',['status'=>409]);if(in_array($old['state'],['cancelled','interrupted'],true))return ['id'=>$id,'state'=>$state,'discarded'=>true];
            $verification=$old['kind']==='verify';if($state==='completed'&&($verification?(!is_array($report)||!isset($report['verified'])||!is_bool($report['verified'])):!self::valid_report($report,$old['target'])))return new WP_Error('report','Invalid report.',['status'=>400]);
            $json=$state==='completed'?wp_json_encode($report):null;if($old['state']===$state&&$old['report']===$json)return ['id'=>$id,'state'=>$state];if($old['state']!=='running')return new WP_Error('stale','Job is no longer running.',['status'=>409]);
            if($wpdb->update($t,['state'=>$state,'report'=>$json],['id'=>$id,'state'=>'running','lease'=>hash('sha256',$lease)])!==1)return new WP_Error('storage','Could not store result.',['status'=>500]);
            if($verification){$wpdb->update(self::domains_table(),['verified'=>$state==='completed'&&$report['verified']?time():0,'created'=>time()],['id'=>$old['domain_id'],'owner'=>(int)$old['owner']]);}
            return ['id'=>$id,'state'=>$state];
        });
    }
    public static function listing(){global $wpdb;$t=self::table();$rows=$wpdb->get_results($wpdb->prepare("SELECT id,target,kind,created,state FROM $t WHERE owner=%d AND created>%d ORDER BY created DESC LIMIT 10",get_current_user_id(),time()-86400),ARRAY_A);$included=false;foreach($rows as &$r){$r['report']=null;if($r['state']==='completed'&&($r['kind']==='verify'||!$included)){$raw=$wpdb->get_var($wpdb->prepare("SELECT report FROM $t WHERE id=%s",$r['id']));$r['report']=$raw?json_decode($raw,true):null;if($r['kind']==='audit')$included=true;}}$response=new WP_REST_Response(['jobs'=>$rows],200);$response->header('Cache-Control','no-store, private');return $response;}
    public static function health(){return ['state'=>'ready','version'=>self::VERSION,'protocol'=>2];}
}
OVLA_Bridge::boot();register_activation_hook(__FILE__,['OVLA_Bridge','install']);register_deactivation_hook(__FILE__,static function(){flush_rewrite_rules(false);});
