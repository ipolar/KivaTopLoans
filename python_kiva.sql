SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE `tbl_log` (
  `log_id` int(11) NOT NULL auto_increment,
  `http_error_code` varchar(255) default NULL,
  `url_error_reason` varchar(255) default NULL,
  `http_request_success_datetime` datetime default NULL,
  `http_request_datetime` datetime default NULL,
  PRIMARY KEY  (`log_id`)
) ENGINE=MyISAM AUTO_INCREMENT=38 DEFAULT CHARSET=latin1;


CREATE TABLE `tbl_scraped_loans` (
  `scraped_loans_id` int(11) NOT NULL auto_increment,
  `scraped_loans_date_scraped` datetime NOT NULL default '0000-00-00 00:00:00',
  `scraped_loans_funded` datetime NOT NULL default '0000-00-00 00:00:00',
  `kiva_id` int(11) default NULL,
  `kiva_status` varchar(255) default NULL,
  `kiva_funded_amount` varchar(100) default NULL,
  `kiva_basket_amount` varchar(100) default NULL,
  `kiva_posted_date` datetime default NULL,
  `log_id` int(11) default NULL,
  `error_text` varchar(255) default NULL,
  `kiva_loan_amount` varchar(100) default NULL,
  PRIMARY KEY  (`scraped_loans_id`),
  UNIQUE KEY `kiva_id` (`kiva_id`)
) ENGINE=MyISAM AUTO_INCREMENT=337 DEFAULT CHARSET=latin1;


CREATE TABLE `tbl_scraped_loans_items` (
  `scraped_loans_items_id` int(11) NOT NULL auto_increment,
  `kiva_id` int(11) default NULL,
  `kiva_status` varchar(255) default NULL,
  `kiva_funded_amount` varchar(100) default NULL,
  `kiva_basket_amount` varchar(100) default NULL,
  `http_error_code` varchar(255) default NULL,
  `url_error_reason` varchar(255) default NULL,
  `http_request_success_datetime` datetime default NULL,
  `http_request_datetime` datetime default NULL,
  PRIMARY KEY  (`scraped_loans_items_id`)
) ENGINE=MyISAM AUTO_INCREMENT=9324 DEFAULT CHARSET=latin1;


SET FOREIGN_KEY_CHECKS = 1;
