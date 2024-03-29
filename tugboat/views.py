#!/bin/sh
#encoding: utf-8
"""
Views
"""

from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from past.builtins import basestring
from builtins import object
from tugboat.client import client
import traceback
from flask import redirect, current_app, request, abort, render_template
from flask_restful import Resource
from webargs import fields
from webargs.flaskparser import parser
import urllib.request, urllib.parse, urllib.error
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import re
from collections import OrderedDict
import adsparser

class IndexView(Resource):
    """
    Return the index page. This is temporary until the app is deployed on its
    own instance.
    """
    def get(self):
        """
        HTTP GET request
        :return: index html page
        """
        return current_app.send_static_file('index.html')


class SimpleClassicView(Resource):
    """for testing, show ads page with single input text field"""
    def get(self):
        return current_app.send_static_file('classic_w_BBB_button.html')

class ComplexClassicView(Resource):
    """for testing, show standard ads search page"""
    def get(self):
        return current_app.send_static_file('fielded_classic_w_BBB_button.html')

class ComplexClassicArXivView(Resource):
    """for testing, show standard ads search page with arXiv classes visible"""
    def get(self):
        return current_app.send_static_file('preprint_service_w_BBB_button.html')

class ComplexClassicPhysicsView(Resource):
    """for testing, show standard ads search page with physics classes visible"""
    def get(self):
        return current_app.send_static_file('physics_service_w_BBB_button.html')

class TranslationValue(object):
    """simple singleton container class to hold translation components

    functions that translation specific parameters typically augment the TranslationValue
    """

    # consider adding field for sort order and other args
    def __init__(self):
        self.search = []
        self.filter= []
        self.error_message = []
        self.warning_message = []
        self.unprocessed_fields = []
        self.sort = ''
        self.facet = []
        self.params = ''

class ClassicSearchRedirectView(Resource):
    """
    End point converts classic search to bumbblebee, returns an http redirect

    Where possible, returned query should be human readable and illustrate what a good query looks like
    """

    def __init__(self):
        super(ClassicSearchRedirectView, self).__init__()
        self.translation = TranslationValue()


        # all the parameters from classic
        # typically integer fields must be represented by Field to allow None values
        # some of these need use type fields.List
        self.api = {
            # the following we currently translate
            'article_sel': fields.Str(required=False),
            'aut_logic': fields.Str(required=False),
            'aut_xct': fields.Str(required=False),
            'author': fields.Str(required=False),
            'data_link': fields.Str(required=False),
            'db_key': fields.Str(required=False),
            'end_entry_day': fields.Field(required=False),
            'end_entry_mon': fields.Field(required=False),
            'end_entry_year': fields.Field(required=False),
            'end_mon': fields.Field(required=False),
            'end_year': fields.Field(required=False),
            'jou_pick': fields.Str(required=False),
            'obj_logic': fields.Str(required=False),
            'object': fields.Str(required=False),
            'open_link': fields.Str(required=False),
            'preprint_link': fields.Str(required=False),
            'qsearch': fields.Str(required=False),
            'return_req': fields.Str(required=False),
            'start_entry_day': fields.Field(required=False),
            'start_entry_mon': fields.Field(required=False),
            'start_entry_year': fields.Field(required=False),
            'start_mon': fields.Field(required=False),
            'start_year': fields.Field(required=False),
            'text': fields.Str(required=False),
            'txt_logic': fields.Str(required=False),
            'title': fields.Str(required=False),
            'ttl_logic': fields.Str(required=False),

            # implementations for the following just create errors
            # perhaps because there is no ads/bumbleebee support yet
            # 6/11/2019 pass it in for the unclassic functionality
            'nr_to_return': fields.Field(required=False),
            'start_nr': fields.Field(required=False),

            # golnaz - 3/5/2018
            'article_link': fields.Str(required=False),
            'gif_link': fields.Str(required=False),
            'article': fields.Str(required=False),
            'simb_obj': fields.Str(required=False),
            'ned_obj': fields.Str(required=False),
            'data_and': fields.Str(required=False),
            'toc_link': fields.Str(required=False),
            'pds_link': fields.Str(required=False),
            'multimedia_link': fields.Str(required=False),
            'ref_link': fields.Str(required=False),
            'citation_link': fields.Str(required=False),
            'associated_link': fields.Str(required=False),
            'lib_link': fields.Str(required=False),
            'ar_link': fields.Str(required=False),
            'aut_note': fields.Str(required=False),
            'spires_link': fields.Str(required=False),
            'group_and': fields.Str(required=False),
            'group_sel': fields.Str(required=False),
            'abstract': fields.Str(required=False),
            'sort': fields.Str(required=False),
            'aut_wt': fields.Field(required=False),
            'obj_wt': fields.Field(required=False),
            'ttl_wt': fields.Field(required=False),
            'txt_wt': fields.Field(required=False),
            'aut_wgt': fields.Str(required=False),
            'obj_wgt': fields.Str(required=False),
            'ttl_wgt': fields.Str(required=False),
            'txt_wgt': fields.Str(required=False),
            'aut_syn': fields.Str(required=False),
            'ttl_syn': fields.Str(required=False),
            'txt_syn': fields.Str(required=False),
            'aut_sco': fields.Str(required=False),
            'ttl_sco': fields.Str(required=False),
            'txt_sco': fields.Str(required=False),
            'aut_req': fields.Str(required=False),
            'obj_req': fields.Str(required=False),
            'ttl_req': fields.Str(required=False),
            'txt_req': fields.Str(required=False),
            'ref_stems': fields.Str(required=False),
            'arxiv_sel': fields.Str(required=False),

            # these can be ignored, at least for now
            'sim_query': fields.Str(required=False),
            'ned_query': fields.Str(required=False),
            'mail_link': fields.Str(required=False),
            'gpndb_obj': fields.Str(required=False),
            'min_score': fields.Str(required=False),
            'lpi_query': fields.Str(required=False),
            'iau_query': fields.Str(required=False),
            'data_type': fields.Str(required=False),
            'adsobj_query': fields.Str(required=False),

            # and the following are not yet translated
            'kwd_wt': fields.Field(required=False),
            'full_wt': fields.Field(required=False),
            'aff_wt': fields.Field(required=False),
            'full_syn': fields.Str(required=False),
            'aff_syn': fields.Str(required=False),
            'kwd_wgt': fields.Str(required=False),
            'full_wgt': fields.Str(required=False),
            'aff_wgt': fields.Str(required=False),
            'kwd_sco': fields.Str(required=False),
            'full_sco': fields.Str(required=False),
            'aff_sco': fields.Str(required=False),
            'kwd_req': fields.Str(required=False),
            'full_req': fields.Str(required=False),
            'aff_req': fields.Str(required=False),
            'aut_logic': fields.Str(required=False),
            'obj_logic': fields.Str(required=False),
            'kwd_logic': fields.Str(required=False),
            'ttl_logic': fields.Str(required=False),
            'txt_logic': fields.Str(required=False),
            'full_logic': fields.Str(required=False),
            'aff_logic': fields.Str(required=False),

            # these are added for myads queryies
            'query_type': fields.Str(required=False),
            'qform': fields.Str(required=False),

            # 11/22 supporting bibcode
            'bibcode': fields.Str(required=False),

            # 12/10 support secondary db
            'db_key2': fields.Str(required=False),

            # 6/22/2020 support bibstem, volume and page
            'bibstem': fields.Str(required=False),
            'year': fields.Str(required=False),
            'volume': fields.Str(required=False),
            'page': fields.Str(required=False),

        }


    def get(self):
        """
        return 302 to bumblebee
        """
        try:
            current_app.logger.info('Classic search redirect received data, headers: {}'.format(request.headers))
            bbb_url=current_app.config['BUMBLEBEE_URL']
            bbb_query = self.translate(request)
            redirect_url = bbb_url + 'search/'+ bbb_query
            current_app.logger.info('translated classic {} to bumblebee {}, {}'.format(request, bbb_query, redirect_url))
            # golnaz 3/11/2018
            # while testing and using curl to see the build url after redirect call, noticed that url gets html encoded,
            # and in particular & become &amp; that BBB does not like, hence switched to render_template to tell it that
            # the url is safe and not encode it
            # but then while testing classic template, realized no encoding was done and so switched back, since
            # it felt redirect was faster and unnoticeable compared to render_template
            return redirect(redirect_url, code=302)
            #return render_template('redirect.html', url=redirect_url), 200
        except Exception as e:
            current_app.logger.error(e.message)
            current_app.logger.error(traceback.format_exc())
            return '<html><body><h2>Error translating classic query</h2> ' + e.message + '<p>' + traceback.format_exc() + '<p>' + str(request) + '</body></html>'


    def parse(self, request):
        """
        Parse the input parameter
        """
        args = parser.parse(self.api, request)
        # group_sel is a special case since we could have repeated entries, (i.e., &group_sel=ARI&group_sel=ESO%2FLib&group_sel=HST)
        # hence need to extract them to a list, and then turn it to a string, since calling parser.parse only parses the first element
        group_sel = request.args.getlist('group_sel', type=str)
        if len(group_sel) > 0:
            args['group_sel'] = ','.join(group_sel)
        # similarly db_key
        db_key = request.args.getlist('db_key', type=str)
        if len(db_key) > 0:
            args['db_key'] = ','.join(db_key)
        # and arxiv_sel
        arxiv_sel = request.args.getlist('arxiv_sel', type=str)
        if len(arxiv_sel) > 0:
            args['arxiv_sel'] = ','.join(arxiv_sel)
        return args

    def translate(self, request):
        """
        Convert all classic search related parameters to ads/bumblebee
        """
        args = self.parse(request)

        if args.get('query_type', None):
            return self.translate_myads_queries(args)

        # functions to translate/process specific parameters
        # consider using reflection to obtain this list
        funcs = [self.translate_authors,
                 self.translate_pubdate, self.translate_entry_date,
                 self.translate_results_subset, self.translate_return_req,
                 self.translate_article_sel, self.translate_database,
                 self.translate_jou_pick, self.translate_group_sel,
                 self.translate_sort, self.translate_to_ignore,
                 self.translate_weights, self.translate_arxiv_sel,
                 self.translate_ref_stems, self.translate_search_docs]
        for f in funcs:
            f(args)  # each may contribute to self.translation singleton

        # functions to deal with the simple cases where only parameter name changes
        self.translate_simple(args, 'object', 'object')
        self.translate_simple(args, 'title', 'title')
        self.translate_simple(args, 'text', 'abs')
        self.translate_simple(args, 'bibcode', 'bibcode')

        # this is a filter on the classic side but in solr search is not treated as such
        self.translate_data_entries(args)

        # translate qsearch as the last item, which is for unfielded form
        # this way qsearch parameter is still in args so that it can be decided which parameters
        # make sense to mark as unprocessed
        self.translate_qsearch(args)

        # combine translation fragments in self.translation to ads/bumblebee parameter string
        if len(self.translation.search) == 0:
            self.translation.search = ['*:*']
        solr_query  = ''.join(self.translation.facet) + '&' if len(self.translation.facet) > 0 else ''
        solr_query += 'q=' + ' '.join(self.translation.search)
        if len(self.translation.filter) > 0:
            solr_query += '&fq=' + '&fq='.join(self.translation.filter)
        if len(self.translation.sort) > 0:
            solr_query += '&sort=' + self.translation.sort
        if len(self.translation.params) > 0:
            solr_query += self.translation.params
        if len(self.translation.error_message) > 0:
            solr_query += '&error_message=' + '&error_message='.join(self.translation.error_message)
        if len(self.translation.warning_message):
            solr_query += '&warning_message=' + '&warning_message='.join(self.translation.warning_message)
        if len(self.translation.unprocessed_fields) :
            solr_query += '&unprocessed_parameter=' + '&unprocessed_parameter='.join(self.translation.unprocessed_fields)
        if len(list(args.keys())):
            # the functions that translate individual parameters use pop to remove parameters from arg list
            # here if there are unprocessed parameters
            # pass their names out ads/bumblebee
            solr_query += '&unprocessed_parameter=' + urllib.parse.quote('Parameters not processed: ' + ' '.join(list(args.keys())))
        # add an extra slash for safari browser
        return solr_query + '/'

    @staticmethod
    def author_exact(args):
        """given an aut_xct value, is it true"""
        value = args.pop('aut_xct', None)
        if value:
            if 'YES' == str(value).upper():
                return True
        return False

    @staticmethod
    def get_logic(classic_param, args):
        """given a logic parameter, return its value canonical form"""
        classic_param_to_logic = {'author': 'aut_logic', 'title': 'ttl_logic',
                                  'text': 'txt_logic', 'object': 'obj_logic',
                                  'bibcode': ''}
        if classic_param in args:
            logic_param = classic_param_to_logic[classic_param]
            value = args.pop(logic_param, None)
            if value:
                value = value.upper()
            return value
        return ''

    @staticmethod
    def supplied(value):
        """check html parameter to see if it is valid"""
        if value is None or (isinstance(value, basestring) and (len(value) == 0 or not value.isdigit())):
            return False
        return True

    def translate_title_for_myads(self, value):
        """ return classic title in the form accept by BBB """
        try:
            # remove the star if there is one at the beginning and call the special parser
            return adsparser.parse_classic_keywords(value.lstrip('*')).decode('utf8')
        except:
            # go with regular tokenizer
            return self.classic_field_to_string(value)[0].lstrip('*')

    def get_db_key_myads_queries(self, args):
        """return db_key or db_key2 from args without removing it"""
        db_key = args.get('db_key', None)
        if db_key is None or db_key == 'ALL':
            db_key2 = args.get('db_key2', None)
            if db_key2:
                return db_key2
        return db_key

    def arxiv_class_addition_myads_queries(self, args):
        """return arxiv query string for myads queries"""
        arxiv_sel = args.pop('arxiv_sel', None)
        if arxiv_sel and self.validate_arxiv_sel(arxiv_sel):
            # if all entries are valid include them, oring them
            arxiv_class = '(' + ' OR '.join(['arxiv_class:' + c + '.*' for c in arxiv_sel.split(',')]) + ')'
            return arxiv_class
        return ''

    def translate_myads_queries(self, args):
        """return query string for the six different myads queries"""

        query_type = args.pop('query_type', None)

        if query_type == 'PAPERS':
            # decide between query #1 and #3 and #4 based on author/title parameters
            authors_str = args.pop('author', None)
            title_str = args.pop('title', None)

            db_key = self.get_db_key_myads_queries(args)
            arxiv_class = self.arxiv_class_addition_myads_queries(args)

            query = None
            # if author is filled and title is empty then it is Weekly authors query (#3)
            if authors_str and not title_str:
                author_query = ' OR '.join(['author:' + x for x in self.classic_field_to_array(authors_str)])
                arxiv_addition = 'bibstem:arxiv %s '%arxiv_class if db_key == 'PRE' else ''
                query = '{arxiv_addition}{author_query}'.format(arxiv_addition=arxiv_addition, author_query=author_query)
                self.translation.sort = urllib.parse.quote('score desc')

            # if title is filled and author is empty then
            # it is either Daily arXiv query (#1) or Weekly keyword (recent papers) query (#4)
            # so then decide on the db_key
            elif title_str and not authors_str:
                # if db_key is DAILY_PRE or PRE then it is Daily arXiv query (#1)
                if (db_key == 'DAILY_PRE' or db_key == 'PRE') and arxiv_class:
                    title = self.translate_title_for_myads(title_str)
                    # OR arxiv classes and title if db_key is DAILY_PRE,
                    # otherwise leave empty which is going to be AND
                    add_or = ' OR ' if db_key == 'DAILY_PRE' else ' '
                    query = 'bibstem:arxiv ({arxiv_class}{add_or}{title})'.format(arxiv_class=arxiv_class, add_or=add_or, title=title)
                    self.translation.sort = urllib.parse.quote('score desc')
                # if db_key is AST or PHY then it is Weekly keyword (recent papers) query (#4)
                elif db_key == 'AST' or db_key == 'PHY':
                    title = self.translate_title_for_myads(title_str)
                    query = '{title}'.format(title=title)
                    self.translation.sort = urllib.parse.quote('entry_date desc')
                else:
                    self.translation.error_message.append('MISSING_REQUIRED_PARAMETER')

            # if both title and author have values, cannot decide which query it is
            elif authors_str and title_str:
                self.translation.error_message.append('UNRECOGNIZABLE_VALUE')

            if query:
                entry_date = self.translate_entry_date(args, append=False)
                start_year = args.pop('start_year', None)
                # see if there is start date and end date, add them in
                if entry_date:
                    query = '{query} {entry_date}'.format(query=query, entry_date=entry_date)
                if start_year:
                    query = '{query} pubdate:[{start_year}-00 TO *]'.format(query=query, start_year=start_year)
                self.translation.search.append(urllib.parse.quote(query))
        else:
            param = None
            # Weekly citations query (#2)
            if query_type == 'CITES':
                func_type = 'citations'
                authors_str = args.pop('author', None)
                if authors_str:
                    param = '(author:%s)'%' '.join(self.classic_field_to_array(authors_str))
                sort_type = 'entry_date desc'
            # Weekly keyword (popular papers) query (#5)
            elif query_type == 'ALSOREADS':
                func_type = 'trending'
                title_str = args.pop('title', None)
                if title_str:
                    param = self.translate_title_for_myads(title_str)
                sort_type = 'score desc'
            # Weekly keyword (most cited) query (#6)
            elif query_type == 'REFS':
                func_type = 'useful'
                title_str = args.pop('title', None)
                if title_str:
                    param = self.translate_title_for_myads(title_str)
                sort_type = 'score desc'
            # none of the known queries
            else:
                func_type = None

            if func_type and param:
                db_key = self.get_db_key_myads_queries(args)
                arxiv_class = self.arxiv_class_addition_myads_queries(args)
                arxiv_addition = 'bibstem:arxiv %s'%arxiv_class if db_key == 'PRE' else None
                query = '{func_type}{param}'.format(func_type=func_type, param=param) if arxiv_addition is None else \
                        '{func_type}({param} {arxiv_addition})'.format(func_type=func_type, param=param, arxiv_addition=arxiv_addition)
                self.translation.search.append(urllib.parse.quote(query))
                self.translation.sort = urllib.parse.quote(sort_type)
            elif not func_type:
                self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
            elif not param:
                self.translation.error_message.append('MISSING_REQUIRED_PARAMETER')

        self.translate_database(args)
        self.translate_database_secondary(args)

        # combine translation fragments in self.translation to ads/bumblebee parameter string
        if len(self.translation.search) == 0:
            self.translation.search = ['*:*']
        solr_query  = ''.join(self.translation.facet) + '&' if len(self.translation.facet) > 0 else ''
        solr_query += 'q=' + ' '.join(self.translation.search)
        if len(self.translation.filter) > 0:
            solr_query += '&fq=' + '&fq='.join(self.translation.filter)
        if len(self.translation.sort) > 0:
            solr_query += '&sort=' + self.translation.sort
        if len(self.translation.error_message) > 0:
            solr_query += '&error_message=' + '&error_message='.join(self.translation.error_message)
        # add an extra slash for safari browser
        return solr_query + '/'

    def translate_authors(self, args):
        """return string with all author search elements

        classic ui allows different and/or between authors and objects so we handle 
        just the author affecting elements here
        """
        connector = ' AND '
        search = ''
        logic = self.get_logic('author', args)
        exact = self.author_exact(args)
        # 5/21 from Alberto: let's switch the author "OR" to an "AND" by default and issue a warning to the user.
        # 10/30/2019 from Alberto: let's recognize the boolean selected by user
        if logic == 'OR':
            connector = ' OR '
        author_field = 'author:'
        if exact:
            author_field = '=author:'
        # one lone parameter should hold all authors from classic
        authors_str = args.pop('author', None)
        if authors_str:
            authors = self.classic_field_to_array(authors_str)
            single_author = ' '.join(authors).replace('"', '')
            if re.match(r'\^', single_author):
                # is it a single author search: ^last, first$
                match = re.findall(r'\^([^$]*)\$', ' '.join(authors).replace('"', ''))
                # yes
                if match:
                    search = '(author:"' + match[0] + '" and author_count:1)'
                    self.translation.search.append(search)
                else:
                    # is it first author search: ^last, first
                    match = re.findall(r'\^([A-Za-z]+,\s+[A-Za-z]+)', ' '.join(authors).replace('"', ''))
                    # yes
                    if match:
                        search = 'author:"' + match[0] + '"'
                        self.translation.search.append(search)
                    else:
                        # is it first author search, but with no first initials
                        match = re.findall(r'\^([A-Za-z\s]+)', ' '.join(authors).replace('"', ''))
                        # yes
                        if match:
                            search = 'author:"' + match[0] + ',"'
                            self.translation.search.append(search)
            # multiple authors
            else:
                search += urllib.parse.quote(author_field) + '('
                for author in authors:
                    search += urllib.parse.quote(author + connector)
                search = search[:-len(urllib.parse.quote(connector))]  # remove final
                search += ')'
                # fields in search are ANDed as of 5/9 and issue a warning
                if len(self.translation.search) > 0:
                    self.translation.search.append('AND')
                self.translation.search.append(search)
                # see the 10/30/2019 comment above
                # if len(authors) > 1 and logic == 'OR':
                #     self.translation.warning_message.append(urllib.quote('AUTHOR_ANDED_WARNING'))

    def translate_simple(self, args, classic_param, bbb_param):
        """process easy to translate fields including title, abstract, and object

        simply change name of parameter and use boolean connector
        """
        connector = ' AND '
        search = ''
        logic = self.get_logic(classic_param, args)
        if logic == 'OR':
            connector = ' OR '
        # one lone parameter should hold all authors from classic
        classic_str = args.pop(classic_param, None)
        if classic_str:
            # note that only for object we allow multiple tokens and apply connector
            # hence for title and abstract no connector is applied
            if classic_param == 'object':
                terms = self.classic_field_to_array(classic_str)
            else:
                terms = self.classic_field_to_string(classic_str)
                # issue a warning for title and abstract if multiple words are specified and OR is selected
                # 10/30/2019 from Alberto: let's recognize the boolean selected by user
                # if len(''.join(terms).split(' ')) > 1 and logic == 'OR':
                #     if classic_param == 'title':
                #         self.translation.warning_message.append(urllib.quote('TITLE_ANDED_WARNING'))
                #     elif classic_param == 'text':
                #         self.translation.warning_message.append(urllib.quote('ABSTRACT_ANDED_WARNING'))
            search += urllib.parse.quote(bbb_param + ':') + '('
            for term in terms:
                search += urllib.parse.quote(term + connector)
            search = search[:-len(urllib.parse.quote(connector))]  # remove final connector
            search += ')'
            # multiple fields in search are ANDed as of 5/9/2018
            if len(self.translation.search) > 0:
                self.translation.search.append('AND')
            self.translation.search.append(search)

    def convert_year_short_to_long(self, year):
        """convert 2-digit year to 4-digit year"""
        # leave these alone, these are indication of min,max years that shall be replaced by *
        if year == 0 or year == 2222:
            return year

        if year > 100:
            return year

        diff_year = datetime.now().year - (datetime.now().year % 100)
        return year + diff_year if year + diff_year <= datetime.now().year + 1 else year + diff_year - 100

    def translate_pubdate(self, args):
        """translate string with pubdate element
        for pubdate date search, only start or end need be specified
        at least one start year or end year must be provided
        unlike entry date search, negative offsets are not supported
        in classic, 2 digit years were permitted
        bumblebee example: pubdate:[1990-01 TO 1990-02]
        """

        start_year = args.pop('start_year', None)
        end_year = args.pop('end_year', None)
        start_month = args.pop('start_mon', None)
        end_month = args.pop('end_mon', None)

        if self.supplied(start_year) is False and self.supplied(end_year) is False:
            return

        # if start is not provided, use beginning of time
        if not self.supplied(start_year):
            start_year = 0
        if not self.supplied(start_month):
            start_month = 1

        # if end is not provided, use end of time
        if not self.supplied(end_year):
            end_year = 2222
            tmp = datetime.now()
            if not self.supplied(end_month):
                end_month = tmp.month
        else:
            if not self.supplied(end_month):
                end_month = 12

        start_year = self.convert_year_short_to_long(int(start_year))
        start_month = int(start_month)
        end_year = self.convert_year_short_to_long(int(end_year))
        end_month = int(end_month)
        # we can use * for solr query if either start_year or end_year are not set
        # did not change the code above that actually set the values if either is missing
        # Y10k problem, but for 2 digit years we want to be clear what years we are searching
        if start_year == 0:
            search = 'pubdate' + urllib.parse.quote(':[* TO {:04d}-{:02}]'.format(end_year, end_month))
        elif end_year == 2222:
            search = 'pubdate' + urllib.parse.quote(':[{:04d}-{:02d} TO *]'.format(start_year, start_month))
        else:
            search = 'pubdate' + urllib.parse.quote(':[{:04d}-{:02d} TO {:04d}-{:02}]'.format(start_year, start_month,
                                                                                        end_year, end_month))
        # fields in search are ANDed as of 5/9
        if len(self.translation.search) > 0:
            self.translation.search.append('AND')
        self.translation.search.append(search)

    def translate_entry_date_start(self, args):
        """ return formatted start date for entry date"""
        try:
            # get the start dates, if specified turned to int,
            # if not init to 0
            start_year = args.pop('start_entry_year', None)
            if not self.supplied(start_year):
                start_year = 0
            else:
                start_year = self.convert_year_short_to_long(int(start_year))
            start_month = args.pop('start_entry_mon', None)
            if not self.supplied(start_month):
                start_month = 0
            else:
                start_month = int(start_month)
            start_day = args.pop('start_entry_day', None)
            if not self.supplied(start_day):
                start_day = 0
            else:
                start_day = int(start_day)
            # is it date or offset date
            date = sum(d > 0 for d in [start_year,start_month,start_day])
            offset = sum(d < 0 for d in [start_year,start_month,start_day])
            if date > 0 and offset > 0:
                self.translation.error_message.append('ENTRY_DATE_OFFSET_ERROR')
                return None
            # if offset has been specified, get current date, subtract the offset, turn into string and return
            if offset > 0:
                today_start = datetime.now()
                today_start = today_start - relativedelta(days=-start_day, months=-start_month, years=-start_year)
                return today_start.strftime("%Y-%m-%d")
            # if any date fields has been specified, turn into string and return
            # beginning of the time is 01-01-01
            if date >= 0:
                start_year = start_year if start_year != 0 else 1
                start_month = start_month if start_month != 0 else 1
                start_day = start_day if start_day != 0 else 1
                if start_year != 1:
                    # 2/13 per Kelly `add one day to the translated entry_date`
                    next_day = datetime(start_year, start_month, start_day)  + relativedelta(days=1)
                    return next_day.strftime('%Y-%m-%d')
                return '{:04d}-{:02d}-{:02d}'.format(start_year, start_month, start_day)
        except:
            self.translation.error_message.append('ENTRY_DATE_NON_NUMERIC_ERROR')
            return None

    def translate_entry_date_end(self, args):
        """ return formatted end date for entry date"""
        try:
            # get the end dates, if specified turned to int,
            # if not init to 0
            end_year = args.pop('end_entry_year', None)
            if not self.supplied(end_year):
                end_year = 0
            else:
                end_year = self.convert_year_short_to_long(int(end_year))
            end_month = args.pop('end_entry_mon', None)
            if not self.supplied(end_month):
                end_month = 0
            else:
                end_month = int(end_month)
            end_day = args.pop('end_entry_day', None)
            if not self.supplied(end_day):
                end_day = 0
            else:
                end_day = int(end_day)
            # is it date or offset date
            date = sum(d > 0 for d in [end_year,end_month,end_day])
            offset = sum(d < 0 for d in [end_year,end_month,end_day])
            if date > 0 and offset > 0:
                self.translation.error_message.append('ENTRY_DATE_OFFSET_ERROR')
                return None
            # if offset has been specified, get current date, subtract the offset, turn into string and return
            if offset > 0:
                today_end = datetime.now()
                today_end = today_end - relativedelta(days=-end_day, months=-end_month, years=-end_year)
                return today_end.strftime("%Y-%m-%d")
            # if no value has been specified for date, get now, turn into string and return
            if date == 0:
                today_end = datetime.now()
                return today_end.strftime("%Y-%m-%d")
            # if any date fields has been specified, turn into string and return
            if date > 0:
                # if year has not been specified get now
                end_year = end_year if end_year != 0 else datetime.now().year
                # depending on if year is specified init to the end of that year, or if no year init to now
                end_month = end_month if end_month != 0 else (datetime.now().month if end_year == datetime.now().year else 12)
                end_day = end_day if end_day != 0 else \
                    (datetime.now().day if end_year == datetime.now().year else calendar.monthrange(end_year, end_month)[1])
                # 2/13 per Kelly `add one day to the translated entry_date`
                next_day = datetime(end_year, end_month, end_day) + relativedelta(days=1)
                return next_day.strftime('%Y-%m-%d')
        except:
            self.translation.error_message.append('ENTRY_DATE_NON_NUMERIC_ERROR')
            return None

    def translate_entry_date(self, args, append=True):
        """ return string for pubdate element
        entry date has a dual functionality, it can be used to enter the date,
        or offset and then the date is computed from it.
        """
        fields = ['start_entry_day', 'start_entry_mon', 'start_entry_year',\
                  'end_entry_day', 'end_entry_mon', 'end_entry_year']

        # at least one entry date field needs to have been populated to continue
        # this is needed for the test side, from the production side this is always false
        if sum([1 for f in fields if f in args]) == 0:
            return
        # if user has set values for any of fields
        add = sum([1 for f in fields if len(args.get(f, '')) > 0]) > 0

        start_date = self.translate_entry_date_start(args)
        end_date = self.translate_entry_date_end(args)
        if start_date is not None and end_date is not None and add:
            if append:
                search = 'entdate' + urllib.parse.quote(':["{}:00:00" TO "{}"]'.format(start_date, end_date))
                # fields in search are ANDed as of 5/9
                if len(self.translation.search) > 0:
                    self.translation.search.append('AND')
                self.translation.search.append(search)
            else:
                return 'entdate:["{}:00:00" TO "{}"]'.format(start_date, end_date)

    def validate_db_key(self, db_key):
        """Validate database selections"""
        valid_db_key = ['AST', 'PHY', 'PRE', 'DAILY_PRE', 'ALL']
        if len(db_key) == 0:
            return False
        entry = db_key.split(',')
        for e in entry:
            if e not in valid_db_key:
                return False
        return True

    def translate_database_validate(self, value):
        """validate and generate facet and filter queries

        only support for ast and phy, bbb does not support arxiv value, classic does not support general
        """
        dict_db = {'AST':       'astronomy',
                   'PHY':       'physics',
                   'PRE':       'e-prints',
                   'DAILY_PRE': 'e-prints',
                   'ALL'      : ''}

        if self.validate_db_key(value):
            # if all entries are valid include them by oring them
            db_key = ''
            # 8/6/2018 -- to view the filters properly in BBB the format for database is as follows
            #       &filter_database_fq_database=OR
            #       &filter_database_fq_database=database:"general"
            #       &filter_database_fq_database=database:"physics"
            #       &fq={!type=aqp v=$fq_database}&fq_database=(database:"general" OR database:"physics")
            if len(self.translation.facet) > 0:
                self.translation.facet.append('&')
            entry = value.split(',')
            for e in entry:
                if e != 'PRE' and e != 'DAILY_PRE' and e != 'ALL':
                    if len(db_key) > 0:
                        db_key += ' OR '
                    if len(self.translation.facet) == 0:
                        self.translation.facet.append('filter_database_fq_database=OR')
                    db_key += 'database:"' + dict_db[e] + '"'
                    self.translation.facet.append('&filter_database_fq_database=' + 'database:"' + dict_db[e] + '"')
            if len(db_key) > 0:
                self.translation.filter.append(urllib.parse.quote('{') + '!' + urllib.parse.quote('type=aqp v=$fq_database}') + \
                                               '&fq_database=(' + urllib.parse.quote(db_key) + ')')
        else:
            # unrecognizable value
            self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
            self.translation.unprocessed_fields.append('db_key')

    def translate_database(self, args):
        """translate which database to use"""
        value = args.pop('db_key', None)
        if value is None:
            return
        self.translate_database_validate(value)

    def translate_database_secondary(self, args):
        """translate which database to use when there is a secondary database defined"""
        value = args.pop('db_key2', None)
        if value is None:
            return
        self.translate_database_validate(value)

    def translate_results_subset(self, args):
        """subset/pagination currently not supported by bumblebee

        provide error message if pagination request is present

        6/11/2019 in the process of implementing unclassic we are adding these in """
        number_to_return = args.pop('nr_to_return', None)
        start_nr = args.pop('start_nr', None)
        # 11/13 From Alberto: Seems that’s what created the problem we are now seeing.  I think we should remove it, right?
        # if number_to_return:
        #     self.translation.params += '&rows=%s'%(number_to_return)
        # if start_nr:
        #     self.translation.params += '&start=%s'%(start_nr)

        # golnaz: hold off for now
        # if number_to_return or start_nr:
        #     self.translation.error_message.append(urllib.quote('Result subset/pagination is not supported'))

    def translate_jou_pick(self, args):
        """translate for refereed, non-refereed"""
        jou_pick = args.pop('jou_pick', None)
        if jou_pick is None:
            # if not provided, include everything in results, which is default
            pass
        elif jou_pick == 'ALL':
            # include everything in results, which is default
            pass
        elif jou_pick == 'NO':
            # 8/6/2018 -- to view the filters properly in BBB the format for property is as follows
            # filter_property_fq_property=AND
            # &filter_property_fq_property=property:"refereed"
            # &fq={!type=aqp v=$fq_property}&fq_property=(property:"refereed")
            if len(self.translation.facet) > 0:
                self.translation.facet.append('&')
            self.translation.facet.append('filter_property_fq_property=AND')
            self.translation.facet.append('&filter_property_fq_property=property:"refereed"')
            # only include refereed journals
            self.translation.filter.append(urllib.parse.quote('{') + '!' + urllib.parse.quote('type=aqp v=$fq_property}') + \
                                           '&fq_property=(' + urllib.parse.quote('property:("refereed")') + ')')
        elif jou_pick == 'EXCL':
            if len(self.translation.facet) > 0:
                self.translation.facet.append('&')
            self.translation.facet.append('filter_property_fq_property=AND')
            self.translation.facet.append('&filter_property_fq_property=property:"not refereed"')
            # only include non-refereed
            self.translation.filter.append(urllib.parse.quote('{') + '!' + urllib.parse.quote('type=aqp v=$fq_property}') + \
                                           '&fq_property=(' + urllib.parse.quote('property:("not refereed")') + ')')
        else:
            self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
            self.translation.unprocessed_fields.append('jou_pick')


    def translate_data_entries(self, args):
        """ Convert all classic data entries search related parameters to ads/bumblebee """
        dict_entries = {'data_link'       : 'esources:*',
                        'article_link'    : 'esources:("PUB_PDF" OR "PUB_HTML" OR "AUTHOR_PDF" OR "AUTHOR_HTML" OR "ADS_PDF" OR "ADS_SCAN")',
                        'article'         : 'esources:("PUB_PDF" OR "PUB_HTML")',
                        'gif_link'        : 'esources:("ADS_SCAN")',
                        'preprint_link'   : 'esources:("EPRINT_HTML")',
                        'toc_link'        : 'property:("TOC")',
                        'ref_link'        : 'reference:*',
                        'citation_link'   : 'citation_count:[1 TO *]',
                        'associated_link' : 'property:("ASSOCIATED")',
                        'simb_obj'        : 'data:("simbad")',
                        'ned_obj'         : 'data:("ned")',
                        'pds_link'        : 'data:("PDS")',
                        'aut_note'        : 'property:("NOTE")',   # need to verify this later, it is being implemented 3/12
                        'lib_link'        : 'property:("LIBRARYCATALOG")',
                        'ar_link'         : 'read_count:[1 TO *]',
                        'multimedia_link' : 'property:("PRESENTATION")',
                        'spires_link'     : 'property:("INSPIRE")',
                        'abstract'        : 'abstract:*',
                        'open_link'       : 'property:("OPENACCESS")'
        }

        search = []
        operator = self.translate_data_and(args)
        if operator is not None:
            # each may contribute to self.translation singleton
            for classic,BBB in dict_entries.items():
                value = args.pop(classic, None)
                if value is None:
                    # if not provided, we do not need to include it in the result
                    pass
                elif value == 'YES':
                    # include entry, first add the operator
                    # NOT comes first, also add operator if there are multiple selection
                    if (operator == 'NOT') or len(search) > 0:
                        search.append(operator)
                    search.append(urllib.parse.quote(BBB))
                else:
                    # unrecognizable value
                    self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
                    self.translation.unprocessed_fields.append(classic)

        if len(search) == 1:
            self.translation.search.append(''.join(search))
        elif len(search) > 1:
            self.translation.search.append('(' + ' '.join(search) + ')')

    def translate_data_and(self, args):
        """ get bibliographic entries operator """
        data_and = args.pop('data_and', None)
        if data_and is None:
            operator = None
        elif data_and == 'ALL':
            # when 'A bibliographic entry' radio button is selected => include everything in results, which is default
            operator = None
        elif data_and == 'NO':
            # when 'At least one of the following (OR)' radio button is selected
            operator = 'OR'
        elif data_and == 'YES':
            # when 'All of the following (AND)' radio button is selected
            operator = 'AND'
        elif data_and == 'NOT':
            # when 'None of the following (NOT)' radio button is selected
            operator = 'NOT'
        else:
            operator = None
            self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
            self.translation.unprocessed_fields.append('data_and')
        return operator

    def validate_group_sel(self, group_sel):
        valid_group_sel = ['ARI', 'CfA', 'CFHT', 'Chandra', 'ESO/Lib', 'ESO/Telescopes', 'Gemini', 'Herschel', 'HST',
                           'ISO', 'IUE', 'JCMT', 'Keck', 'Leiden', 'LPI', 'Magellan', 'NOAO', 'NRAO', 'NRAO/Telescopes',
                           'ROSAT', 'SDO', 'SMA', 'Spitzer', 'Subaru', 'Swift', 'UKIRT', 'USNO', 'VSGC', 'XMM']
        if len(group_sel) == 0:
            return False
        entry = group_sel.split(',')
        for e in entry:
            if e not in valid_group_sel:
                return False
        return True

    def translate_group_sel(self, args):
        """ Convert all classic group entries search related parameters to ads/bumblebee """
        operator = self.translate_group_and(args)
        if operator is not None:
            value = args.pop('group_sel', None)
            if value is None:
                return
            if self.validate_group_sel(value):
                # if all entries are valid include them, adding in the selected operator
                # 8/6/2018 -- to view the filters properly in BBB the format for bibgroup is as follows
                # filter_bibgroup_facet_fq_bibgroup_facet=AND
                # &filter_bibgroup_facet_fq_bibgroup_facet=bibgroup_facet:"CfA"
                # &fq={!type=aqp v=$fq_bibgroup_facet}&fq_bibgroup_facet=(bibgroup_facet:"CfA")
                if len(self.translation.facet) > 0:
                    self.translation.facet.append('&')
                self.translation.facet.append('filter_bibgroup_facet_fq_bibgroup_facet=' + operator)
                group_sel = ''
                entry = value.split(',')
                for e in entry:
                    if (operator == 'NOT') or len(group_sel) > 0:
                        group_sel += ' ' + operator + ' '
                    group_sel += '"' + e + '"'
                    self.translation.facet.append('&filter_bibgroup_facet_fq_bibgroup_facet=' + 'bibgroup_facet:"' + e + '"')
                if len(group_sel) > 0:
                    self.translation.filter.append(urllib.parse.quote('{') + '!' + urllib.parse.quote('type=aqp v=$fq_bibgroup_facet}') + \
                        '&fq_bibgroup_facet=(' + urllib.parse.quote_plus('bibgroup_facet:({})'.format(group_sel)) + ')')
            else:
                # unrecognizable value
                self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
                self.translation.unprocessed_fields.append('group_sel')

    def translate_group_and(self, args):
        """ set group entries operator """
        group_and = args.pop('group_and', None)
        if group_and is None:
            operator = None
        elif group_and == 'ALL':
            # when 'All Groups' radio button is selected => include everything in results, which is default
            operator = None
        elif group_and == 'NO':
            # when 'At least one of the following groups (OR)' radio button is selected
            operator = 'OR'
        elif group_and == 'YES':
            # when 'All of the following groups (AND)' radio button is selected
            operator = 'AND'
        else:
            operator = None
            self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
            self.translation.unprocessed_fields.append('group_and')

        return operator

    def translate_return_req(self, args):
        """if return_req parameter is provided, it must be 'result' or None

        return error if any other value is supplied

        """
        return_req = args.pop('return_req', None)
        if return_req is None:
            pass
        elif return_req == 'result':
            pass
        elif return_req == 'no_params':
            pass
        else:
            self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
            self.translation.unprocessed_fields.append('return_req')


    def translate_article_sel(self, args):
        article_sel = args.pop('article_sel', None)
        if article_sel is None:
            pass
        elif article_sel == 'YES':
            # 8/6/2018 -- to view the filters properly in BBB the format for doctype is as follows
            # filter_doctype_facet_hier_fq_doctype=AND
            # &filter_doctype_facet_hier_fq_doctype=doctype_facet_hier:"0/Article"
            # &fq={!type=aqp v=$fq_doctype}&fq_doctype=(doctype_facet_hier:"0/Article")
            if len(self.translation.facet) > 0:
                self.translation.facet.append('&')
            self.translation.facet.append('filter_doctype_facet_hier_fq_doctype=AND')
            self.translation.facet.append('&filter_doctype_facet_hier_fq_doctype=' +
                                          urllib.parse.quote_plus('doctype_facet_hier:"0/Article"'))
            # only include article journals
            self.translation.filter.append(urllib.parse.quote('{') + '!' + urllib.parse.quote('type=aqp v=$fq_doctype}') + \
                                           '&fq_doctype=(' + urllib.parse.quote_plus('doctype_facet_hier:"0/Article"') + ')')
        else:
            self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
            self.translation.unprocessed_fields.append('article_sel')


    def translate_qsearch(self, args):
        """translate qsearch parameter from single input form on classic_w_BBB_button.html

        return nonfielded metadata search query
        """
        REGEX_UNFILDED_MATCH = OrderedDict([
            (re.compile(r"^(bibcode)?.*([12][089]\d\d[A-Z\.0-9&]{15})$", re.IGNORECASE), r'bibcode:"%s"'),
            (re.compile(r"^(:?bibcode=)(([12][089?][\d?][\d?][A-Z\.&*0-9\s]+[OoAa]?[RrNn]?[Dd]?)+)$", re.IGNORECASE), r'bibcode:"%s"'),
            (re.compile(r"^title[=\s:]+(.*)$", re.IGNORECASE), r'title:"%s"'),
            (re.compile(r"^author[s]*[=\s:]+(.*)$", re.IGNORECASE), r'author:"%s"'),
            (re.compile(r"^[doi]?.*(10\..*)$", re.IGNORECASE), r'doi:"%s"'),
            (re.compile(r"^year.*([12][089]\d\d-[12][089]\d\d)$", re.IGNORECASE), r'year:%s'),
            (re.compile(r"^year.*([12][089]\d\d)$", re.IGNORECASE), r'year:%s'),
            (re.compile(r"^([12][089]\d\d)$", re.IGNORECASE), r'year:%s'),
            (re.compile(r"^(.*)$", re.IGNORECASE), r'%s'),
        ])
        value = args.pop('qsearch', None)
        if value:
            qsearch = ''
            for i, key in enumerate(REGEX_UNFILDED_MATCH):
                match = key.search(value)
                if match:
                    qsearch = REGEX_UNFILDED_MATCH[key]%(match.group(1 if i > 1 else 2))
                    break
            if len(qsearch) > 0:
                self.translation.search.append(urllib.parse.quote_plus(qsearch))


    def translate_sort(self, args):
        """ translate sort parameter """
        dict_sort = {'SCORE'         : 'score desc',
                     'AUTHOR'        : 'first_author desc',
                     'NDATE'         : 'date desc',
                     'ODATE'         : 'date asc',
                     'BIBCODE'       : 'bibcode desc',
                     'RBIBCODE'      : 'bibcode asc',
                     'ENTRY'         : 'entry_date desc',
                     'CITATIONS'     : 'citation_count desc',
                     'AUTHOR_CNT'    : 'author_count desc',
                     'SBIBCODE'      : 'bibcode desc',
                     'READS'         : 'read_count desc',
                     'AR_SCORE'      : 'read_count desc',
                     'NORMCITATIONS' : 'citation_count_norm desc',
                     'NORMSCORE'     : '',
                     'NONE'          : '',
                     'PAGE'          : 'bibcode asc',
                     'RPAGE'         : 'bibcode desc',
        }

        value = args.pop('sort', None)
        if value is None:
            self.translation.sort = urllib.parse.quote('date desc, bibcode desc')
            return

        for classic,BBB in dict_sort.items():
            if value == classic:
                self.translation.sort = urllib.parse.quote(BBB)
                return

        # unrecognizable value
        self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
        self.translation.unprocessed_fields.append('sort')

    def translate_to_ignore(self, args):
        """ remove the fields that is being ignored in some cases an unprocessed message is issued """
        classic_ignored_fields = {'sim_query'    : 'All object queries include SIMBAD and NED search results.',
                                  'ned_query'    : 'All object queries include SIMBAD and NED search results.',
                                  'min_score'    : 'Please note Min Score is deprecated.',
                                  'mail_link'    : 'Please note Mail Order Links is deprecated.',
                                  # From Alberto 3/12 regarding data_type: we'll want it available for API queries, so it's for later
                                  'data_type'    : 'Selected data format was ignored please select export function here.',
                                  'lpi_query'    : '',
                                  'iau_query'    : '',
                                  'gpndb_obj'    : '',
                                  'adsobj_query' : '',
                                  'aff_logic'    : '',
                                  'aff_req'      : '',
                                  'aff_sco'      : '',
                                  'aff_syn'      : '',
                                  'aff_wgt'      : '',
                                  'aff_wt'       : '',
                                  'kwd_logic'    : '',
                                  'kwd_req'      : '',
                                  'kwd_sco'      : '',
                                  'kwd_wgt'      : '',
                                  'kwd_wt'       : '',
                                  'full_logic'   : '',
                                  'full_req'     : '',
                                  'full_sco'     : '',
                                  'full_syn'     : '',
                                  'full_wgt'     : '',
                                  'full_wt'      : '',
                                  'qform'        : '',

        }
        for key,value in classic_ignored_fields.items():
            set_key = args.pop(key, None)
            if (key == 'sim_query' or key == 'ned_query'):
                # if it is checked, do nothing
                if (set_key is not None):
                    continue
                # if no object search is entered, do nothing
                # note that this function is called before function that analyzes object
                # hence object should still be in args
                if ('object' in list(args.keys()) and len(args['object']) == 0):
                    continue
                # go down to display a message if either of queries is unchecked
                # and an object search is defined
            # only produce a message if a value is set for min_score
            if key == 'min_score' and set_key == '':
                continue
            if key == 'mail_link' and set_key == None:
                continue
            # only produce a message if other than default
            # 6/11/2019 lets not ignore this anymore
            # 10/30/2019 as per Alberto, we are back to ignoring this param, kinda, we are accepting value of `SHORT`
            if key == 'data_type' and set_key == 'SHORT':
                self.translation.params += '&format=' + set_key
                continue
            if set_key is None:
                continue
            if key not in self.translation.unprocessed_fields:
                self.translation.unprocessed_fields.append(key)

    def translate_weights(self, args):
        """ check the weight parameters """
        # these weights are need to be in default settings
        # if they have been modified by the user, issue an unprocessed message
        dict_weights_default = {'aut_syn'  :  'YES',
                                'ttl_syn'  :  'YES',
                                'txt_syn'  :  'YES',
                                'aut_wt'   :  '1.0',
                                'obj_wt'   :  '1.0',
                                'ttl_wt'   :  '0.3',
                                'txt_wt'   :  '3.0',
                                'aut_wgt'  :  'YES',
                                'obj_wgt'  :  'YES',
                                'ttl_wgt'  :  'YES',
                                'txt_wgt'  :  'YES',
                                'ttl_sco'  :  'YES',
                                'txt_sco'  :  'YES',
                                'aut_sco'  :  'NO',
                                'aut_req'  :  'NO',
                                'obj_req'  :  'NO',
                                'ttl_req'  :  'NO',
                                'txt_req'  :  'NO',
        }
        dict_weights_of_type = {'syn' : 'Synonym Replacement',
                                'wt'  : 'Relative Weights',
                                'wgt' : 'Use For Weighting',
                                'sco' : 'Weighted Scoring',
                                'req' : 'Require Field for Selection',

        }
        # some of the calls are coming from else where that have no weight specified
        # if that is the case do not show any unprocessed message
        one_weight_present = False
        not_default = []
        for key,value in dict_weights_default.items():
            if key in args:
                one_weight_present = True
                set_key = args.pop(key, None)
                # if differs from default added to the list
                if set_key != value:
                    type = key.split('_')[1]
                    if dict_weights_of_type[type] not in not_default:
                        not_default.append(dict_weights_of_type[type])
            # if not in args it means it was not selected, compare to see if default is YES
            # if so added it in
            else:
                if 'NO' != value:
                    type = key.split('_')[1]
                    if dict_weights_of_type[type] not in not_default:
                        not_default.append(dict_weights_of_type[type])
        if len(not_default) > 0 and one_weight_present:
            if args.get('qsearch', None) is not None:
                # if this was for an unfielded query just display one general message
                self.translation.unprocessed_fields.append(urllib.parse.quote('One or more weighted parameter(s)'))
            else:
                for err in not_default:
                    self.translation.unprocessed_fields.append(urllib.parse.quote(err))



    def validate_arxiv_sel(self, arxiv_sel):
        """Validate arXiv selections"""
        valid_arxiv_sel = ['astro-ph', 'cond-mat', 'cs', 'gr-qc', 'hep-ex', 'hep-lat', 'hep-ph', 'hep-th',
                           'math', 'math-ph', 'nlin', 'nucl-ex', 'nucl-th', 'physics', 'quant-ph', 'q-bio']
        if len(arxiv_sel) == 0:
            return False
        entry = arxiv_sel.split(',')
        for e in entry:
            if e not in valid_arxiv_sel:
                return False
        return True

    def translate_arxiv_sel(self, args):
        """Convert all classic arXiv entries search related parameters to ads/bumblebee"""
        dict_arxiv = {'astro-ph'  :  'Astrophysics',
                      'cond-mat'  :  'Condensed Matter',
                      'cs'        :  'Computer Science',
                      'gr-qc'     :  'General Relativity and Quantum Cosmology',
                      'hep-ex'    :  'High Energy Physics - Experiment',
                      'hep-lat'   :  'High Energy Physics - Lattice',
                      'hep-ph'    :  'High Energy Physics - Phenomenology',
                      'hep-th'    :  'High Energy Physics - Theory',
                      'math'      :  'Mathematics',
                      'math-ph'   :  'Mathematical Physics',
                      'nlin'      :  'Nonlinear Sciences',
                      'nucl-ex'   :  'Nuclear Experiment',
                      'nucl-th'   :  'Nuclear Theory',
                      'physics'   :  'Physics',
                      'quant-ph'  :  'Quantum Physics',
                      'q-bio'     :  'Quantitative Biology',
        }
        value = args.pop('arxiv_sel', None)
        if value is None:
            return
        # consider arXiv only if other dbs are not selected
        filter = urllib.parse.unquote(''.join(self.translation.filter))
        if 'database:"astronomy"' in filter or 'database:"physics"' in filter:
            # 3/19/2019 remove the warning, as per Alberto.
            # self.translation.warning_message.append(
            #     urllib.quote('when the astronomy or physics databases are selected, the arXiv selection is ignored'))
            return
        if self.validate_arxiv_sel(value):
            # if all entries are valid include them, oring them
            entry = value.split(',')
            # if all the classes are selected apply arxiv:(*) query
            if len(entry) == len(dict_arxiv):
                self.translation.search.append('property:(' + urllib.parse.quote("EPRINT_OPENACCESS") + ')')
            else:
                arxiv_sel = ''
                for e in entry:
                    if len(arxiv_sel) > 0:
                        arxiv_sel += ' OR '
                    arxiv_sel += '"' + dict_arxiv[e].lower() + '"'
                self.translation.search.append('keyword:(' + urllib.parse.quote(arxiv_sel) + ')')
        else:
            # unrecognizable value
            self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
            self.translation.unprocessed_fields.append('arxiv_sel')


    def parse_bibstem(self, value):
        """
        parse bibstem, no need for validating, just pass it to BBB, if any bibstem has been specified
        """
        #
        bibstem = ''
        # there is A&A, GCN1, CLic2, JPhy3, JPhy4
        # or it could be something like A&A....33
        match = re.findall('([-+]*[A-Za-z&.0-9]{2,9})', value)
        # yes
        if match:
            ref_stems_positive = ''
            ref_stems_negative = ''
            for e in match:
                if e.startswith('-'):
                    if len(ref_stems_negative) > 0:
                        ref_stems_negative += ' OR '
                    ref_stems_negative += urllib.parse.quote('"' + e[1:] + '"')
                else:
                    if len(ref_stems_positive) > 0:
                        ref_stems_positive += ' OR '
                    if e.startswith('+'):
                        ref_stems_positive += urllib.parse.quote('"' + e[1:] + '"')
                    else:
                        ref_stems_positive += urllib.parse.quote('"' + e + '"')
            if len(ref_stems_positive) > 0 and len(ref_stems_negative) > 0:
                bibstem = 'bibstem:(' + ref_stems_positive + ') AND ' + '-bibstem:(' + ref_stems_negative + ')'
            elif len(ref_stems_positive) > 0:
                bibstem = 'bibstem:(' + ref_stems_positive + ')'
            elif len(ref_stems_negative) > 0:
                bibstem = '-bibstem:(' + ref_stems_negative + ')'
        else:
            self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
            self.translation.unprocessed_fields.append(value)

        return bibstem

    def translate_ref_stems(self, args):
        """
        BBB: bibstem:(ApJ.. OR AJ..); classic: ref_stems="ApJ..,AJ..."
        list of comma-separated ADS bibstems to return, e.g. ref_stems="ApJ..,AJ..."
        """
        value = args.pop('ref_stems', None)
        if value is None:
            return
        # not validating, just pass it to BBB, if any bibstem has been specified
        ref_stems = ''
        if len(value) > 0:
            self.translation.search.append(self.parse_bibstem(value))

    def translate_search_docs(self, args):
        """
        translate four params bibstem, year, volume, and page
        BBB: bibstem:(ApJ.. OR AJ..); classic: bibstem="ApJ..,AJ..."
        BBB: year:[2019 TO 2020]; classic: year="2019-2020" OR
        BBB: year:2019; classic: year=2019
        """
        search = ''
        value = args.pop('bibstem', None)
        if value:
            if len(value) > 0:
                search = self.parse_bibstem(value)

        value = args.pop('year', None)
        if value:
            if len(value) > 0:
                match = re.search(r'^([12][089]\d\d-[12][089]\d\d|[12][089]\d\d)$', value)
                if match:
                    value = value.split('-')
                    if len(value) == 2:
                        year = '[' + value[0] + ' TO ' + value[1] + ']'
                    else:
                        year = value[0]
                    search += urllib.parse.quote(' AND ' if len(search)>0 else '') + 'year:' + year
                else:
                    self.translation.error_message.append('UNRECOGNIZABLE_VALUE')
                    self.translation.unprocessed_fields.append(value)

        value = args.pop('page', None)
        if value:
            if len(value) > 0:
                search += urllib.parse.quote(' AND ' if len(search)>0 else '') + 'page:' + urllib.parse.quote('"' + value + '"')

        value = args.pop('volume', None)
        if value:
            if len(value) > 0:
                search += urllib.parse.quote(' AND ' if len(search)>0 else '') + 'volume:' + urllib.parse.quote('"' + value + '"')

        if len(search) > 0:
            self.translation.search.append(search)

    @staticmethod
    def classic_field_to_array(value):
        """ convert authors/objects/title/abstract search words from classic to list"""
        value = urllib.parse.unquote(value)
        value = value.replace('\r\n', ';')
        values = value.split(';')
        for i in range(0, len(values)):
            negate = False
            # remove any whitespace before +/- if any
            values[i] = re.sub(r"^\s+", "", values[i], flags=re.UNICODE)
            # now remove +/- if any, note the negative to attach it back
            if values[i].startswith('+') or values[i].startswith('-'):
                negate = values[i].startswith('-')
                values[i] = values[i][1:]
            # remove any whitespace before/after the words
            values[i] = re.sub(r"^\s+|\s+$", "", values[i], flags=re.UNICODE)
            # if not an empty string and if not quoted, then quoted
            if len(values[i]) > 0:
                if (values[i].startswith('"') and values[i].endswith('"')) is False:
                    # always surround by double quotes if not already
                    values[i] = ('-' if negate else '') + '"' + values[i] + '"'
        # remove any empty strings
        values = [_f for _f in values if _f]
        return values
    
    @staticmethod
    def classic_field_to_string(value):
        """ convert authors/objects/title/abstract search words from classic to list"""
        value = urllib.parse.unquote(value)
        value = value.replace('\r\n', ';')
        values = value.split(';')
        for i in range(0, len(values)):
            negate = False
            # remove any whitespace before +/- if any
            values[i] = re.sub(r"^\s+", "", values[i], flags=re.UNICODE)
            # now remove +/- if any, note the -
            if values[i].startswith('+') or values[i].startswith('-'):
                negate = values[i].startswith('-')
                values[i] = values[i][1:]
            # remove any whitespace before/after the words
            values[i] = re.sub(r"^\s+|\s+$", "", values[i], flags=re.UNICODE)
            # if not an empty string
            if len(values[i]) > 0:
                values[i] = ('-' if negate else '') + values[i]
        # remove any empty strings
        values = [_f for _f in values if _f]
        # concatenate and return in a list with one element
        return [' '.join(values)]

class BumblebeeView(Resource):
    """
    End point that is used to forward a search result page from ADS Classic
    to ADS Bumblebee
    """

    def get_post_data(self, request):
        """
        Attempt to coerce POST json data from the request, falling
        back to the raw data if json could not be coerced.
        :param request: flask.request

        :return: dict
        """
        try:
            post_data = request.get_json(force=True)
        except:
            post_data = request.values

        return post_data

    def post(self):
        """
        HTTP GET request

        There are two simple steps:
            1. Send a query to myads-service in 'store-query' that contains
               the list of bibcodes in the user's ADS Classic search
            2. Return a URL with the relevant queryid that the user can be
               forwarded to

        When the user clicks the URL, it will use execute-query to run the
        relevant query via Solr's Bigquery.

        Returns:
        302: redirect to the relevant URL

        :return: str
        """

        # Setup the data
        current_app.logger.info('Received data, headers: {}'.format(request.headers))
        data = self.get_post_data(request)

        if not isinstance(data, list):
            current_app.logger.error(
                'User passed incorrect format: {}, {}'.format(type(data), data)
            )
            abort(400)
        elif not all([isinstance(i, str) for i in data]):
            current_app.logger.error(
                'List contains non-unicode characters: {}'.format(data)
            )
            abort(400)

        bigquery_data = {
            'bigquery': ['bibcode\n' + '\n'.join(data)],
            'q': ['*:*'],
            'fq': ['{!bitset}']
        }

        items = list(request.headers.items())
        headers = {k: v for k, v in list(request.headers.items())}

        # POST the query
        # https://api.adsabs.harvard.edu/v1/vault/query
        current_app.logger.info('Contacting vault/query ' + str(current_app.config['TESTING']))
        r = client().post(
        current_app.config['VAULT_QUERY_URL'],
        data = bigquery_data,
        headers = headers
        )

        if r.status_code != 200:
            current_app.logger.warning(
                'vault/query returned non-200 exit status: {}'.format(r.text)
            )
            return r.text, r.status_code, list(r.headers.items())

        # Get back a query id
        current_app.logger.info('vault/query returned: {}'.format(r.json()))
        query_id = r.json()['qid']

        # Formulate the url based on the query id
        redirect_url = '{BBB_URL}search/q=*%3A*&__qid={query_id}'.format(
            BBB_URL=current_app.config['BUMBLEBEE_URL'],
            query_id=query_id
        )
        current_app.logger.info(
            'Returning redirect: {}'.format(redirect_url)
        )

        # Return the query id to the user
        return {'redirect': redirect_url}, 200
