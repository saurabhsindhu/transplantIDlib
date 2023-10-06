import pathlib
import re

from environs import Env
from flask_babel import gettext as _
from kerko import extractors, transformers
from kerko.composer import Composer
from kerko.renderers import TemplateRenderer
from kerko.specs import BadgeSpec, CollectionFacetSpec, FieldSpec, SortSpec
from whoosh.fields import BOOLEAN, STORED

from .extractors import InCollectionBoostExtractor, MatchesTagExtractor
from .transformers import extra_field_cleaner

# pylint: disable=invalid-name

env = Env()
env.read_env()


class Config():

    def __init__(self):
        app_dir = pathlib.Path(env.str('FLASK_APP')).parent.absolute()

        # Get configuration values from the environment.
        self.SECRET_KEY = env.str('SECRET_KEY')
        self.KERKO_ZOTERO_API_KEY = env.str('KERKO_ZOTERO_API_KEY')
        self.KERKO_ZOTERO_LIBRARY_ID = env.str('KERKO_ZOTERO_LIBRARY_ID')
        self.KERKO_ZOTERO_LIBRARY_TYPE = env.str('KERKO_ZOTERO_LIBRARY_TYPE')
        self.KERKO_DATA_DIR = env.str(
            'KERKO_DATA_DIR', str(app_dir / 'data' / 'kerko'))

        # Set other configuration variables.
        self.LOGGING_HANDLER = 'default'

        self.LIBSASS_INCLUDES = [
            str(pathlib.Path(__file__).parent.parent / 'static' /
                'src' / 'vendor' / 'bootstrap' / 'scss'),
            str(pathlib.Path(__file__).parent.parent / 'static' / 'src' /
                'vendor' / '@fortawesome' / 'fontawesome-free' / 'scss'),
        ]

        self.BABEL_DEFAULT_LOCALE = 'en_US'
        self.KERKO_WHOOSH_LANGUAGE = 'en_US'
        self.KERKO_ZOTERO_LOCALE = 'en_US'
        self.BABEL_DEFAULT_TIMEZONE = 'EST'

        self.HOME_URL = 'https://www.myast.org/'
        self.HOME_URL2 = '/'
        self.HOME_TITLE = _("TransplantID")
        self.HOME_SUBTITLE = _(
            "Research and Innovation to fulfil the potential of TransplantID")
        self.ABOUT_WHAT_WE_DO = 'https://edtechhub.org/what-we-do/'
        self.ABOUT_WHERE_WE_WORK = 'https://edtechhub.org/where-we-work/'
        self.ABOUT_OUR_TEAM = 'https://edtechhub.org/our-team/'
        self.ABOUT_STRATEGIC_ADVISORY = 'https://edtechhub.org/strategic-advisory-board/'
        self.ABOUT_SPECIALIST_NETWORK = 'https://edtechhub.org/specialist-network/'
        self.TOOLS_DATABASE_URL = 'https://www.myast.org/communities-practice/infectious-disease-community-practice-idcop'
        self.EVIDENCE_ABOUT_URL = 'https://twitter.com/TransplantIDNet/'
        self.EVIDENCE_LIBRARY_URL = 'https://docs.edtechhub.org/lib/'
        self.EVIDENCE_COUNTRY_ENGAGEMENT_URL = 'https://edtechhub.org/where-we-work/'
        self.EVIDENCE_TOPIC_AREAS_URL = 'https://edtechhub.org/our-topic-areas/'
        self.EVIDENCE_RESEARCH_PORTFOLIO_URL = 'https://edtechhub.org/evidence/edtech-hub-research-portfolio/'
        self.EVIDENCE_SANDBOXES_URL = 'https://edtechhub.org/sandboxes/'
        self.EVIDENCE_HELPDESK_URL = 'https://edtechhub.org/edtech-hub-helpdesk/'
        self.BLOG_URL = 'https://doi.org/10.1093/ofid/ofad081'
        self.CONNECT_WITH_US_URL = 'https://transplantid.net/WhoWeAre.html'
        self.CONNECT_WITH_US_NEWSLETTER_URL = 'https://edtechhub.org/newsletter/'
        self.CONNECT_WITH_US_EVENTS_URL = 'https://edtechhub.org/events/'
        self.CONNECT_WITH_US_CONTACT_URL = 'https://transplantid.net/UndertheHood.html'

        self.NAV_TITLE = _("")
        self.KERKO_TITLE = _("TransplantID")
        self.KERKO_PRINT_ITEM_LINK = True
        self.KERKO_PRINT_CITATIONS_LINK = True
        self.KERKO_RESULTS_FIELDS = [
            'id', 'attachments', 'bib', 'data', 'preview']
        self.KERKO_RESULTS_ABSTRACTS = False
        self.KERKO_RESULTS_ABSTRACTS_MAX_LENGTH = 500
        self.KERKO_RESULTS_ABSTRACTS_MAX_LENGTH_LEEWAY = 40
        self.KERKO_TEMPLATE_LAYOUT = 'app/layout.html.jinja2'
        self.KERKO_TEMPLATE_SEARCH = 'app/search.html.jinja2'
        self.KERKO_TEMPLATE_SEARCH_ITEM = 'app/search-item.html.jinja2'
        self.KERKO_TEMPLATE_ITEM = 'app/item.html.jinja2'
        self.KERKO_DOWNLOAD_ATTACHMENT_NEW_WINDOW = True
        self.KERKO_OPEN_IN_ZOTERO_APP = True
        self.KERKO_OPEN_IN_ZOTERO_WEB = True
        self.KERKO_RELATIONS_INITIAL_LIMIT = 50
        self.KERKO_FEEDS = ['']
        self.KERKO_FEEDS_MAX_DAYS = 0

        # CAUTION: The URL's query string must be changed after any edit to the CSL
        # style, otherwise zotero.org might still use a previously cached version of
        # the file.
        self.KERKO_CSL_STYLE = 'https://docs.edtechhub.org/static/dist/csl/eth_apa.xml?202012301815'

        self.KERKO_COMPOSER = Composer(
            whoosh_language=self.KERKO_WHOOSH_LANGUAGE,
            exclude_default_facets=[
                'facet_tag', 'facet_link', 'facet_item_type', 'facet_year'],
            exclude_default_fields=['data'],
            default_item_exclude_re=r'^_exclude$',
            default_child_include_re=r'^(_publish|publishPDF)$',
            default_child_exclude_re=r'',
            facet_initial_limit=6,
            facet_initial_limit_leeway=4,
        )

        # Replace the default 'data' extractor to strip unwanted data from the Extra field.
        self.KERKO_COMPOSER.add_field(
            FieldSpec(
                key='data',
                field_type=STORED,
                extractor=extractors.TransformerExtractor(
                    extractor=extractors.RawDataExtractor(),
                    transformers=[extra_field_cleaner]
                ),
            )
        )

        # Add field for storing the formatted item preview used on search result
        # pages. This relies on the CSL style's in-text citation formatting and only
        # makes sense using our custom CSL style!
        self.KERKO_COMPOSER.add_field(
            FieldSpec(
                key='preview',
                field_type=STORED,
                extractor=extractors.TransformerExtractor(
                    extractor=extractors.ItemExtractor(
                        key='citation', format_='citation'),
                    # Zotero wraps the citation in a <span> element (most probably
                    # because it expects the 'citation' format to be used in-text),
                    # but that <span> has to be removed because our custom CSL style
                    # causes <div>s to be nested within. Let's replace that <span>
                    # with the same markup that the 'bib' format usually provides.
                    transformers=[
                        lambda value: re.sub(
                            r'^<span>', '<div class="csl-entry">', value, count=1),
                        lambda value: re.sub(
                            r'</span>$', '</div>', value, count=1),
                    ]
                )
            )
        )

        # Add extractors for the 'alternate_id' field.
        self.KERKO_COMPOSER.fields['alternate_id'].extractor.extractors.append(
            extractors.TransformerExtractor(
                extractor=extractors.ItemDataExtractor(key='extra'),
                transformers=[
                    transformers.find(
                        regex=r'^\s*EdTechHub.ItemAlsoKnownAs\s*:\s*(.*)$',
                        flags=re.IGNORECASE | re.MULTILINE,
                        max_matches=1,
                    ),
                    transformers.split(sep=';'),
                ]
            )
        )
        self.KERKO_COMPOSER.fields['alternate_id'].extractor.extractors.append(
            extractors.TransformerExtractor(
                extractor=extractors.ItemDataExtractor(key='extra'),
                transformers=[
                    transformers.find(
                        regex=r'^\s*KerkoCite.ItemAlsoKnownAs\s*:\s*(.*)$',
                        flags=re.IGNORECASE | re.MULTILINE,
                        max_matches=1,
                    ),
                    transformers.split(sep=' '),
                ]
            )
        )
        self.KERKO_COMPOSER.fields['alternate_id'].extractor.extractors.append(
            extractors.TransformerExtractor(
                extractor=extractors.ItemDataExtractor(key='extra'),
                transformers=[
                    transformers.find(
                        regex=r'^\s*shortDOI\s*:\s*(\S+)\s*$',
                        flags=re.IGNORECASE | re.MULTILINE,
                        max_matches=0,
                    ),
                ]
            )
        )

        # Guidelines type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_guidelines',
                filter_key='guidelines',
                title=_('GUIDELINES'),
                weight=1,
                collection_key='DMZGXQPK',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # Textbook type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_textbooks',
                filter_key='textbooks',
                title=_('TEXTBOOKS'),
                weight=2,
                collection_key='TQLYTNTG',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # ORGANISMS type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_organisms',
                filter_key='organisms',
                title=_('ORGANISMS'),
                weight=3,
                collection_key='EX4SAVUI',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # PATIENT EDUCATION type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_patient_education',
                filter_key='patient_education',
                title=_('PATIENT EDUCATION'),
                weight=4,
                collection_key='I9SWX7JX',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # DIAGNOSTICS facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_diagnostics',
                title=_('DIAGNOSTICS'),
                filter_key='diagnostics',
                weight=5,
                collection_key='GZMLE9CP',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # DRUGS AND THERAPIES facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_drugs_and_therapies',
                title=_('DRUGS AND THERAPIES'),
                filter_key='drugs_and_therapies',
                weight=6,
                collection_key='XE782DPL',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # PREVENTION facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_prevention',
                title=_('PREVENTION'),
                filter_key='prevention',
                weight=7,
                collection_key='JMJCPZ8T',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # SYNDROMES AND CONDITIONS facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_syndromes_and_conditions',
                title=_('SYNDROMES AND CONDITIONS'),
                filter_key='syndromes_and_conditions',
                weight=8,
                collection_key='LENWYRWR',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # SOLID ORGANS AND MCSS facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_solid_organs_and_mcss',
                title=_('SOLID ORGANS AND MCSS'),
                filter_key='solid_organs_and_mcss',
                weight=9,
                collection_key='R6DI3TQT',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # HEME/ONC AND CELLULAR THERAPIES facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_heme-onc_and_cellular_therapies',
                title=_('HEME-ONC AND CELLULAR THERAPIES'),
                filter_key='heme-onc_and_cellular_therapies',
                weight=10,
                collection_key='FEXGFAWR',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # EDUCATION type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_education',
                filter_key='education',
                title=_('EDUCATION'),
                weight=11,
                collection_key='ZFP5DRQS',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # Covid-19 type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_covid-19',
                filter_key='covid-19',
                title=_('COVID-19'),
                weight=12,
                collection_key='ICABG5DW',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # Within-country contexts type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_frailty',
                filter_key='frailty',
                title=_('FRAILTY'),
                weight=13,
                collection_key='DZB8PTRD',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # ARTICLE OF THE MONTH type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_article_of_the_month',
                filter_key='article_of_the_month',
                title=_('ARTICLE OF THE MONTH'),
                weight=14,
                collection_key='XSEHIBPU',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # Within-country contexts type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_atc_2023_top_papers_in_tid',
                filter_key='atc_2023_top_papers_in_tid',
                title=_('ATC 2023 Top Papers in TID'),
                weight=15,
                collection_key='ENFCTNHS',
                initial_limit=6,
                initial_limit_leeway=4,
            )
        )

        # # Language of publication type facet.
        # self.KERKO_COMPOSER.add_facet(
        #     CollectionFacetSpec(
        #         key='facet_language_of_publication',
        #         filter_key='language_of_publication',
        #         title=_('Language of publication'),
        #         weight=8,
        #         collection_key='ZNNITHFH',
        #         initial_limit=6,
        #         initial_limit_leeway=4,
        #     )
        # )

        # # Publisher and type facet.
        # self.KERKO_COMPOSER.add_facet(
        #     CollectionFacetSpec(
        #         key='facet_publisher_type',
        #         filter_key='publisher_type',
        #         title=_('Publisher and type'),
        #         weight=9,
        #         collection_key='N6HGZU24',
        #         initial_limit=6,
        #         initial_limit_leeway=4,
        #     )
        # )

        # # Research method type facet.
        # self.KERKO_COMPOSER.add_facet(
        #     CollectionFacetSpec(
        #         key='facet_research_method',
        #         filter_key='research_method',
        #         title=_('Research method'),
        #         weight=10,
        #         collection_key='9WEL59XM',
        #         initial_limit=6,
        #         initial_limit_leeway=4,
        #     )
        # )

        # # COVID and reopening of schools type facet.
        # self.KERKO_COMPOSER.add_facet(
        #     CollectionFacetSpec(
        #         key='facet_covid_and_reopening_of_schools',
        #         filter_key='covid_and_reopening_of_schools',
        #         title=_('COVID and reopening of schools'),
        #         weight=11,
        #         collection_key='NRS95TC8',
        #         initial_limit=6,
        #         initial_limit_leeway=4,
        #     )
        # )

        # # Topic Area facet.
        # self.KERKO_COMPOSER.add_facet(
        #     CollectionFacetSpec(
        #         key='facet_topic_area',
        #         title=_('Topic Area'),
        #         filter_key='topic_area',
        #         weight=12,
        #         collection_key='W6YXX3J6',
        #         initial_limit=6,
        #         initial_limit_leeway=4,
        #     )
        # )

        # # Focus Countries facet.
        # self.KERKO_COMPOSER.add_facet(
        #     CollectionFacetSpec(
        #         key='facet_focus_countries',
        #         title=_('Focus Countries'),
        #         filter_key='focus_countries',
        #         weight=13,
        #         collection_key='F29UQFBX',
        #         initial_limit=0,
        #         initial_limit_leeway=0,
        #     )
        # )

        # EdTech Hub flag and badge.
        self.KERKO_COMPOSER.add_field(
            FieldSpec(
                key='edtechhub',
                field_type=BOOLEAN(stored=True),
                extractor=extractors.InCollectionExtractor(
                    collection_key='BFS3UXT4'),
            )
        )
        self.KERKO_COMPOSER.add_badge(
            BadgeSpec(
                key='edtechhub',
                field=self.KERKO_COMPOSER.fields['edtechhub'],
                activator=lambda field, item: bool(item.get(field.key)),
                renderer=TemplateRenderer(
                    'app/_hub-badge.html.jinja2', badge_title=_('Published by The EdTech Hub')
                ),
                weight=100,
            )
        )
        # "Internal document" flag and badge.
        self.KERKO_COMPOSER.add_field(
            FieldSpec(
                key='internal',
                field_type=BOOLEAN(stored=True),
                extractor=MatchesTagExtractor(pattern=r'^_internal$'),
            )
        )
        self.KERKO_COMPOSER.add_badge(
            BadgeSpec(
                key='internal',
                field=self.KERKO_COMPOSER.fields['internal'],
                activator=lambda field, item: item.get(field.key, False),
                renderer=TemplateRenderer(
                    'app/_text-badge.html.jinja2', text=_('Internal<br />document')
                ),
                weight=10,
            )
        )
        # "Coming soon" flag and badge.
        self.KERKO_COMPOSER.add_field(
            FieldSpec(
                key='comingsoon',
                field_type=BOOLEAN(stored=True),
                extractor=MatchesTagExtractor(pattern=r'^_comingsoon$'),
            )
        )
        self.KERKO_COMPOSER.add_badge(
            BadgeSpec(
                key='comingsoon',
                field=self.KERKO_COMPOSER.fields['comingsoon'],
                activator=lambda field, item: item.get(field.key, False),
                renderer=TemplateRenderer(
                    'app/_text-badge.html.jinja2', text=_('Coming<br >soon')
                ),
                weight=20,
            )
        )

        # Boost factor for every field of any EdTech Hub publication.
        self.KERKO_COMPOSER.add_field(
            FieldSpec(
                # Per whoosh.writing.IndexWriter.add_document() usage.
                key='_boost',
                field_type=None,  # Not to be added to the schema.
                extractor=InCollectionBoostExtractor(
                    collection_key='BFS3UXT4', boost_factor=5.0),
            )
        )

        # Sort option based on the EdTech Hub flag.
        self.KERKO_COMPOSER.add_sort(
            SortSpec(
                key='hub_desc',
                label=_(''),
                weight=4,
                fields=[
                    # self.KERKO_COMPOSER.fields['edtechhub'],
                    self.KERKO_COMPOSER.fields['sort_date'],
                    self.KERKO_COMPOSER.fields['sort_creator'],
                    self.KERKO_COMPOSER.fields['sort_title']
                ],
                reverse=[
                    True,
                    False,
                    False,
                    False
                ],
            )
        )


class DevelopmentConfig(Config):

    def __init__(self):
        super().__init__()

        self.CONFIG = 'development'
        self.DEBUG = True
        # Don't bundle/minify static assets.
        self.ASSETS_DEBUG = env.bool('ASSETS_DEBUG', False)
        self.LIBSASS_STYLE = 'expanded'
        self.LOGGING_LEVEL = env.str('LOGGING_LEVEL', 'DEBUG')
        # self.EXPLAIN_TEMPLATE_LOADING = True


class ProductionConfig(Config):

    def __init__(self):
        super().__init__()

        self.CONFIG = 'production'
        self.DEBUG = False
        self.ASSETS_DEBUG = env.bool('ASSETS_DEBUG', False)
        self.ASSETS_AUTO_BUILD = False
        self.LOGGING_LEVEL = env.str('LOGGING_LEVEL', 'WARNING')
        self.GOOGLE_ANALYTICS_ID = 'G-EXXEPNEBH8'
        self.LIBSASS_STYLE = 'compressed'


CONFIGS = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
