<?php
class OpenViST_Technical_Discovery {public static function roles(){return ["infrastructure"=>["label"=>"Infrastructure"],"builder"=>["label"=>"Builder tools"],"app"=>["label"=>"Apps"]];}
    public static function role_links($category='') {
        $html='<nav class="ov-project-roles" aria-label="Browse by project role"><span>Browse by project role</span>';
        foreach(self::roles() as $key=>$role){
            $html.='<form method="get" action="'.esc_url(get_post_type_archive_link('hp_listing')).'"><input type="hidden" name="ov_view" value="all">';
            if($category!=='')$html.='<input type="hidden" name="ov_category" value="'.esc_attr($category).'">';
            $html.='<button type="submit" name="ov_role" value="'.esc_attr($key).'">'.esc_html($role['label']).'</button></form>';
        }
        return $html.'</nav>';
    }
}
