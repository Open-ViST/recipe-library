<?php
// Exact helper methods from Directory UI 0.4.108 for WordPress integration checks.
class OpenViST_Public_Integrity {
    public static function listing_description($id) {
        $description=trim((string)get_post_meta($id,'_openvist_editorial_meta_description',true));
        if(!OpenViST_Directory_UI::is_safe_public_summary($description))$description=OpenViST_Directory_UI::directory_summary($id);
        return OpenViST_Directory_UI::trim_characters(trim(preg_replace('/\s+/u',' ',wp_strip_all_tags((string)$description))),180);
    }
    /** One description owner for managed listing templates, including legacy theme tags. */
    public static function listing_head($header,$id) {
        if(defined('WPSEO_VERSION')||defined('RANK_MATH_VERSION')||defined('SEOPRESS_VERSION')||defined('AIOSEO_VERSION'))return $header;
        $description=self::listing_description($id);
        if($description===''||stripos($header,'</head>')===false)return $header;
        $header=preg_replace_callback('/<meta\b(?:"[^"]*"|\'[^\']*\'|[^\'">])*>/i',static function($match){
            $tag=new WP_HTML_Tag_Processor($match[0]);
            if($tag->next_tag('META')&&strtolower((string)$tag->get_attribute('name'))==='description')return '';
            return $match[0];
        },$header);
        return preg_replace_callback('~</head>~i',static function()use($description){return '<meta name="description" content="'.esc_attr($description).'">'."\n".'</head>';},$header,1);
    }
}
