export type Lang = 'fa' | 'en';
export const langs: Lang[] = ['fa', 'en'];

export const ui = {
  fa: {
    dir: 'rtl',
    locale: 'fa_IR',
    site: 'هومودین',
    tagline: 'یک سؤال آشنا دربارهٔ AI و علم، با یک آزمایش یا شاهد دیدنی.',
    home: 'خانه',
    episodes: 'قسمت‌ها',
    blog: 'وبلاگ',
    other: 'English',
    companion: 'همراه قسمت',
    deepDive: 'عمیق‌تر: داده و روش',
    watch: 'تماشا در یوتیوب',
    deck: 'دک ضبط',
    soon: 'به‌زودی در یوتیوب',
    sources: 'منابع',
    datasets: 'داده‌ها',
    boundary: 'مرز ادعا',
    posts: 'نوشته‌های این قسمت',
    latest: 'تازه‌ترین نوشته‌ها',
    allEpisodes: 'همهٔ قسمت‌ها',
    readMore: 'بخوان',
    rss: 'خوراک RSS',
    published: 'انتشار',
    code: 'کد و دادهٔ قسمت‌ها در GitHub',
  },
  en: {
    dir: 'ltr',
    locale: 'en_US',
    site: 'Homodyne',
    tagline: 'One familiar question about AI and science, answered with an experiment you can see.',
    home: 'Home',
    episodes: 'Episodes',
    blog: 'Blog',
    other: 'فارسی',
    companion: 'Episode companion',
    deepDive: 'Deep dive: data and method',
    watch: 'Watch on YouTube',
    deck: 'Recording deck',
    soon: 'Coming soon on YouTube',
    sources: 'Sources',
    datasets: 'Datasets',
    boundary: 'Claim boundary',
    posts: 'Posts for this episode',
    latest: 'Latest posts',
    allEpisodes: 'All episodes',
    readMore: 'Read',
    rss: 'RSS feed',
    published: 'Published',
    code: 'Episode code and data on GitHub',
  },
} as const;

export const REPO = 'https://github.com/AshE-96/homodyne';

export const formatDate = (d: Date, lang: Lang) =>
  d.toLocaleDateString(lang === 'fa' ? 'fa-IR' : 'en-GB', { year: 'numeric', month: 'long', day: 'numeric' });
