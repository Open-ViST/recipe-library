<?php
/**
 * Plugin Name: OpenViST Tools
 * Description: Free local JSON and CSV tools. Input processing runs in browser workers.
 * Version: 0.1.0
 * Requires at least: 6.5
 * Requires PHP: 8.0
 * Author: OpenViST
 * License: GPL-2.0-or-later
 */
defined('ABSPATH') || exit;
final class OpenViST_Tools {
    const VERSION = '0.1.0';
    public static function catalogue() {
        return [
            'json-validator'=>['title'=>'JSON Validator & Formatter','intro'=>'Validate, format or minify JSON while preserving the original numeric tokens.','detail'=>'Duplicate object keys are rejected. Maximum nesting: 100 levels; maximum values: 100,000. Formatting preserves number and string spellings.'],
            'csv-comparator'=>['title'=>'CSV Comparator','intro'=>'Compare two CSV files by an identifier column and find added, removed and modified rows.','detail'=>'Comma-separated CSV with a header row. Headers must be nonempty and unique; each row must have the same column count. Identifiers must be nonempty and unique in each file.'],
            'duplicate-finder'=>['title'=>'Duplicate & Conflict Finder','intro'=>'Find repeated identifiers and identifiers associated with different text values in CSV or JSON.','detail'=>'Select two different, literal field names. Both fields must contain nonempty strings. JSON input must be an array of objects. Positions are one-based data record positions.'],
        ];
    }
    public static function route() {
        $value = get_query_var('openvist_tool', '');
        return $value === 'index' || isset(self::catalogue()[$value]) ? $value : '';
    }
    public static function rules() {
        add_rewrite_rule('^tools/?$', 'index.php?openvist_tool=index', 'top');
        add_rewrite_rule('^tools/(json-validator|csv-comparator|duplicate-finder)/?$', 'index.php?openvist_tool=$matches[1]', 'top');
    }
    public static function url($slug = '') { return home_url('/tools/'.($slug && $slug !== 'index' ? $slug.'/' : '')); }
    public static function title() { $route=self::route();return $route && $route!=='index' ? self::catalogue()[$route]['title'] : 'Free browser tools'; }
    public static function boot() {
        add_action('init',[__CLASS__,'rules']);
        add_filter('query_vars',static function($vars){$vars[]='openvist_tool';return $vars;});
        add_action('pre_get_posts',static function($query){
            if(!$query->is_main_query())return;
            $route=(string)$query->get('openvist_tool');
            if($route!=='index'&&!isset(self::catalogue()[$route]))return;
            $query->is_home=false;$query->is_page=false;$query->is_singular=false;$query->is_archive=false;$query->is_404=false;
            $query->set('post__in',[0]);$query->set('posts_per_page',1);$query->set('no_found_rows',true);
        },100);
        add_filter('pre_handle_404',static function($handled,$query){if(!self::route())return $handled;$query->is_404=false;status_header(200);return true;},10,2);
        add_filter('redirect_canonical',static function($url){return self::route()?false:$url;});
        add_filter('pre_get_document_title',static function($title){return self::route()?self::title().' | OpenViST':$title;},999);
        add_filter('openvist_brand_metadata_enabled',static function($enabled){return self::route()?false:$enabled;});
        add_filter('template_include',static function($template){return self::route()?__DIR__.'/template.php':$template;},PHP_INT_MAX);
        add_filter('body_class',static function($classes){if(self::route())$classes=array_merge($classes,['ovt-page','openvist-public-ui']);return array_unique($classes);});
        add_action('wp_enqueue_scripts',static function(){
            if(!self::route())return;
            wp_enqueue_style('openvist-tools',plugins_url('assets/tools.css',__FILE__),[],self::VERSION);
            wp_enqueue_script('openvist-tools',plugins_url('assets/tools-ui.js',__FILE__),[],self::VERSION,true);
            wp_add_inline_script('openvist-tools','window.ovtConfig='.wp_json_encode(['worker'=>plugins_url('assets/tools-worker.js',__FILE__).'?ver='.self::VERSION]).';','before');
        },1200);
        add_action('wp_head',[__CLASS__,'metadata'],2);
        add_action('wp',static function(){if(self::route())remove_action('wp_head','rel_canonical');});
        add_filter('openvist_navigation_links',static function($links){
            $result=[];foreach($links as $label=>$path){$result[$label]=$path;if($label==='Recipes')$result['Tools']='/tools/';}
            if(!isset($result['Tools']))$result['Tools']='/tools/';return $result;
        });
        add_action('wp_sitemaps_init',static function($server){
            if(!class_exists('WP_Sitemaps_Provider'))return;
            $provider=new class extends WP_Sitemaps_Provider {
                public function __construct(){$this->name='openvist-tools';$this->object_type='openvist-tools';}
                public function get_url_list($page_num,$object_subtype='') {if((int)$page_num!==1||(string)get_option('blog_public')!=='1')return []; $list=[['loc'=>OpenViST_Tools::url()]];foreach(OpenViST_Tools::catalogue() as $slug=>$tool)$list[]=['loc'=>OpenViST_Tools::url($slug)];return $list;}
                public function get_max_num_pages($object_subtype=''){return (string)get_option('blog_public')==='1'?1:0;}
            };
            // The site's conservative sitemap plugin filters unknown providers.
            // Restore only these four explicitly maintained public Tools URLs.
            add_filter('wp_sitemaps_add_provider',static function($candidate,$name)use($provider){return $name==='openvist-tools'?$provider:$candidate;},120,2);
            $server->registry->add_provider('openvist-tools',$provider);
        });
    }
    public static function metadata() {
        $route=self::route();if(!$route)return;
        $title=self::title().' | OpenViST';
        $description=$route==='index'?'Free browser tools for JSON validation, CSV comparison and duplicate detection. Process inputs locally without an account.':self::catalogue()[$route]['intro'];
        echo '<link rel="canonical" href="'.esc_url(self::url($route)).'">' . "\n";
        echo '<meta name="description" content="'.esc_attr($description).'">' . "\n";
        foreach(['og:title'=>$title,'og:description'=>$description,'og:url'=>self::url($route),'og:type'=>'website','og:site_name'=>'OpenViST'] as $key=>$value)echo '<meta property="'.esc_attr($key).'" content="'.esc_attr($value).'">' . "\n";
        echo '<meta name="twitter:card" content="summary">' . "\n";
    }
}
OpenViST_Tools::boot();
register_activation_hook(__FILE__,static function(){OpenViST_Tools::rules();flush_rewrite_rules(false);});
register_deactivation_hook(__FILE__,static function(){flush_rewrite_rules(false);});
