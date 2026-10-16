<?php
/**
 * Plugin Name: OpenViST Tools
 * Description: Free local data, encoding and checksum tools. Processing runs locally in the browser.
 * Version: 0.3.1
 * Requires at least: 6.5
 * Requires PHP: 8.0
 * Author: OpenViST
 * License: GPL-2.0-or-later
 */
defined('ABSPATH') || exit;
final class OpenViST_Tools {
    const VERSION = '0.3.1';
    public static function catalogue() {
        return [
            'json-compare'=>['title'=>'JSON Compare','intro'=>'Compare two JSON documents by structure and find added, removed or modified values.','detail'=>'Object key order is ignored. Arrays are compared by zero-based index. Number spellings are exact: 1 and 1.0 differ, with no rounding of large numbers. Strings are compared after JSON unescaping. Duplicate keys are rejected. Maximum 100 nesting levels, 100,000 values per input and 10,000 changes. Paths use JSON Pointer; an empty path means the root. Added or removed containers are reported once. Result snippets are JSON source strings, not rounded parsed values. The report is not a JSON Patch.'],
            'base64'=>['title'=>'Base64 Encoder & Decoder','intro'=>'Encode text or a file as Base64, or decode Base64 as UTF-8 text or a binary download.','detail'=>'Standard Base64 requires padding; Base64url uses the unpadded URL-safe alphabet. Whitespace and noncanonical padding bits are rejected. Text is encoded as UTF-8. Files are read as their exact bytes. Base64 is not encryption.'],
            'url-encoder'=>['title'=>'URL Encoder & Decoder','intro'=>'Encode or decode a URL component and inspect query parameters, including repeated names.','detail'=>'Component encoding uses percent escapes and %20 for spaces. Component decoding preserves literal + signs; query inspection treats + as a space. Query inspection accepts at most 20,000 parameters. Results preserve parameter order and repeated names. No URL is requested. Malformed percent escapes and invalid UTF-8 are rejected.'],
            'sha256-checksum'=>['title'=>'SHA-256 Checksum Calculator','intro'=>'Calculate a SHA-256 checksum from text or a file and compare it with an expected value locally.','detail'=>'Files are hashed byte for byte, including line endings and any BOM. Pasted text is encoded as UTF-8; browser editing may normalize line endings. Optional comparisons require 64 hexadecimal characters. A matching hash only establishes equality to the supplied checksum, not source authenticity. Requires HTTPS and Web Crypto.'],
            'json-validator'=>['title'=>'JSON Validator & Formatter','intro'=>'Validate, format or minify JSON while preserving the original numeric tokens.','detail'=>'Duplicate object keys are rejected. Maximum nesting: 100 levels; maximum values: 100,000. Formatting preserves number and string spellings.'],
            'csv-comparator'=>['title'=>'CSV Comparator','intro'=>'Compare two CSV files by an identifier column and find added, removed and modified rows.','detail'=>'Comma-separated CSV with a header row. Headers must be nonempty and unique; each row must have the same column count. Identifiers must be nonempty and unique in each file.'],
            'duplicate-finder'=>['title'=>'Duplicate & Conflict Finder','intro'=>'Find repeated identifiers and identifiers associated with different text values in CSV or JSON.','detail'=>'Select two different, literal field names. Both fields must contain nonempty strings. JSON input must be an array of objects. Positions are one-based data record positions.'],
            'text-diff'=>['title'=>'Text Diff','intro'=>'Compare two texts line by line and identify additions, removals and unchanged lines.','detail'=>'Maximum 2,000 lines per input. Line endings are compared as LF. Case, spaces and Unicode spelling are preserved. Final newline presence is reported separately. The result is a readable comparison, not a patch file.'],
            'csv-json-converter'=>['title'=>'CSV ↔ JSON Converter','intro'=>'Convert CSV records to JSON or flat JSON objects to CSV, with optional column selection.','detail'=>'CSV values remain strings. For JSON to CSV, missing fields and null become empty cells. Selected values must be scalar; nested arrays and objects are rejected. Formula-like string cells are prefixed with an apostrophe by default.'],
            'sitemap-inspector'=>['title'=>'Sitemap Inspector','intro'=>'Inspect a sitemap XML file, extract URLs and find duplicates and common structural issues locally.','detail'=>'Accepts XML urlset and sitemapindex files up to 2 MiB and 20,000 entries. DTD declarations are rejected. These are local structural checks, not complete XSD validation, live link checking or an indexing guarantee.'],
        ];
    }
    public static function route() {
        $value = get_query_var('openvist_tool', '');
        return $value === 'index' || isset(self::catalogue()[$value]) ? $value : '';
    }
    public static function rules() {
        add_rewrite_rule('^tools/?$', 'index.php?openvist_tool=index', 'top');
        add_rewrite_rule('^tools/('.implode('|',array_keys(self::catalogue())).')/?$', 'index.php?openvist_tool=$matches[1]', 'top');
    }
    public static function url($slug = '') { return home_url('/tools/'.($slug && $slug !== 'index' ? $slug.'/' : '')); }
    public static function title() { $route=self::route();return $route && $route!=='index' ? self::catalogue()[$route]['title'] : 'Free browser tools'; }
    public static function boot() {
        add_action('init',[__CLASS__,'rules']);
        add_action('init',static function(){if(get_option('ovt_route_version')!==self::VERSION){flush_rewrite_rules(false);update_option('ovt_route_version',self::VERSION,false);}},20);
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
            $deps=[];
            if(self::route()==='sitemap-inspector'){wp_enqueue_script('openvist-tools-xml',plugins_url('assets/sitemap-dom.js',__FILE__),[],self::VERSION,true);$deps[]='openvist-tools-xml';}
            wp_enqueue_script('openvist-tools',plugins_url('assets/tools-ui.js',__FILE__),$deps,self::VERSION,true);
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
            // Restore these explicitly maintained public Tools URLs.
            add_filter('wp_sitemaps_add_provider',static function($candidate,$name)use($provider){return $name==='openvist-tools'?$provider:$candidate;},120,2);
            $server->registry->add_provider('openvist-tools',$provider);
        });
    }
    public static function metadata() {
        $route=self::route();if(!$route)return;
        $title=self::title().' | OpenViST';
        $description=$route==='index'?'Free local tools for JSON, CSV, text, Base64, URL encoding, SHA-256 and sitemap inspection. Process inputs in your browser without an account.':self::catalogue()[$route]['intro'];
        echo '<link rel="canonical" href="'.esc_url(self::url($route)).'">' . "\n";
        echo '<meta name="description" content="'.esc_attr($description).'">' . "\n";
        foreach(['og:title'=>$title,'og:description'=>$description,'og:url'=>self::url($route),'og:type'=>'website','og:site_name'=>'OpenViST'] as $key=>$value)echo '<meta property="'.esc_attr($key).'" content="'.esc_attr($value).'">' . "\n";
        echo '<meta name="twitter:card" content="summary">' . "\n";
    }
}
OpenViST_Tools::boot();
register_activation_hook(__FILE__,static function(){OpenViST_Tools::rules();flush_rewrite_rules(false);update_option('ovt_route_version',OpenViST_Tools::VERSION,false);});
register_deactivation_hook(__FILE__,static function(){flush_rewrite_rules(false);});
