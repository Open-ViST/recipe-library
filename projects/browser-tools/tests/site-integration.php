<?php
// Run only in a disposable WordPress installation, never on the production site.
require dirname(__DIR__).'/openvist-tools.php';
require __DIR__.'/fixtures/listing-head.php';
require __DIR__.'/fixtures/role-links.php';
class OpenViST_Directory_UI {
 public static function is_safe_public_summary($value){return trim($value)!==''&&!preg_match('/Category:|Vendor:/i',$value);}
 public static function directory_summary($id){return 'Specific developer overview based on the published project profile.';}
 public static function trim_characters($value,$max){return mb_substr($value,0,$max);}
}
function ov_assert($condition,$label){if(!$condition)throw new Exception($label);echo "PASS $label\n";}
register_post_type('hp_listing',['public'=>true,'has_archive'=>'site','rewrite'=>['slug'=>'site']]);
$id=wp_insert_post(['post_type'=>'hp_listing','post_status'=>'publish','post_title'=>'Test listing']);
update_post_meta($id,'_openvist_editorial_meta_description','Project $1: an SDK for <builders> & documented API tasks.');
$old='<head><meta content="Category: X > Vendor: Y" name="description"><META NAME=description content=generic><meta property="og:description" content="Social summary"><meta name="robots" content="noindex"><link rel="canonical" href="https://example.com/site/project/"></head>';
$head=OpenViST_Public_Integrity::listing_head($old,$id);
$processor=new WP_HTML_Tag_Processor($head);$descriptions=[];
while($processor->next_tag('META'))if(strtolower((string)$processor->get_attribute('name'))==='description')$descriptions[]=$processor->get_attribute('content');
ov_assert(count($descriptions)===1,'One standard description after replacing legacy duplicates');
ov_assert($descriptions[0]==='Project $1: an SDK for & documented API tasks.','Description escapes safely, strips markup and preserves dollar signs');
ov_assert(str_contains($head,'og:description')&&str_contains($head,'noindex')&&str_contains($head,'rel="canonical"'),'Social, robots and canonical tags retained');
update_post_meta($id,'_openvist_editorial_meta_description','Category: Generic; Vendor: Account');
ov_assert(str_contains(OpenViST_Public_Integrity::listing_head($old,$id),'Specific developer overview'),'Unsafe legacy description uses specific public fallback');
ov_assert(OpenViST_Public_Integrity::listing_head('<header>no head</header>',$id)==='<header>no head</header>','No head means no rewrite');
$html=OpenViST_Technical_Discovery::role_links('ai');
ov_assert(substr_count($html,'<form')===3&&!str_contains($html,'<a '),'Role shortcuts use forms instead of faceted links');
ov_assert(substr_count($html,'name="ov_category" value="ai"')===3&&str_contains($html,'name="ov_role" value="builder"'),'Role forms preserve category and role filters');
register_post_type('ov_recipe',['public'=>true,'rewrite'=>['slug'=>'recipes']]);
$recipe=wp_insert_post(['post_type'=>'ov_recipe','post_status'=>'publish','post_name'=>'compare-json-object-paths-python','post_title'=>'Compare JSON objects']);
ov_assert(str_contains(OpenViST_Tools::context('json-compare'),esc_url(get_permalink($recipe))),'Published related recipe resolves to its real permalink');
wp_update_post(['ID'=>$recipe,'post_password'=>'fixture']);
ov_assert(!str_contains(OpenViST_Tools::context('json-compare'),esc_url(get_permalink($recipe))),'Password-protected recipe is excluded');
define('WPSEO_VERSION','fixture');ov_assert(OpenViST_Public_Integrity::listing_head($old,$id)===$old,'Full SEO suites retain metadata ownership');
