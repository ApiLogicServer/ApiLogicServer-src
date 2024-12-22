import React, { useEffect, useState } from 'react';
import { Container, Typography, Button, CircularProgress, Box } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import { ISection, IPageData } from './interfaces.tsx';
import { Section } from './sections/Section.tsx';
import Header from './Header.tsx';
import { useDataProvider } from 'react-admin';
import theme from '../themes/default.tsx';


function Loading() {
    return (
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" height="100vh">
            <CircularProgress />
            <Typography variant="h6" style={{ marginTop: '20px' }}>
                Loading...
            </Typography>
        </Box>
    );
}

const Page: React.FC<IPageData> = ({ id, name, SectionList, ...props }) => {
    document.title = name;
    let index = 0;

    return (
        <>
            <Header title={name} SectionList={SectionList} />
            <Container id={id} sx={{ margin: '0px', paddingTop: '4em' }} maxWidth={false}>
                {SectionList?.sort((a: ISection, b: ISection) => a.order - b.order).map((section: ISection) => {
                    index += 1;
                    section.index = index;
                    return <Section key={index} section={section} />;
                })}
            </Container>
        </>
    );
};

const PageList = ({ pages, setSelectedPage }: { pages: IPageData[]; setSelectedPage: any }) => {
    return pages.map((page: IPageData) => (
        <div key={page.id}>
            <Button onClick={() => setSelectedPage(page)}>{page.name}</Button>
        </div>
    ));
};

const ignoreSpa = () => {
    sessionStorage.removeItem('raSpa');
    window.location.href = window.location.href.split('#')[0];
};

const SpApp = () => {
    const [pages, setPages] = useState<IPageData[]>([]);
    const [selectedPage, setSelectedPage] = useState<IPageData | null>(null);
    const [loading, setLoading] = useState(true);
    const dataProvider = useDataProvider();

    useEffect(() => {
        setLoading(true);
        dataProvider
            .getList('SPAPage', {
                pagination: { page: 1, perPage: 10 },
                meta: { include: ['SectionList'] },
            })
            .then((response) => {
                const pages = response.data || [];
                if (pages.length === 1) {
                    setSelectedPage(pages[0]);
                }
                setPages(pages);
            })
            .catch((error) => {
                console.error('DataProvider error', error);
                ignoreSpa();
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    if (loading) {
        return <Loading />;
    }

    if (pages.length === 0) {
        sessionStorage.removeItem('raSpa');
        return (
            <Typography>
                No page data found
                <Button onClick={ignoreSpa}>Return to the main app</Button>
            </Typography>
        );
    }

    if (selectedPage) {
        return <Page {...selectedPage} />;
    }

    return <PageList pages={pages} setSelectedPage={setSelectedPage} />;
};

const App = () => (
    <ThemeProvider theme={theme}>
        <SpApp />
    </ThemeProvider>
);

export default App;