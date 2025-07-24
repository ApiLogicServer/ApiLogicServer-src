    const [loading, setLoading] = React.useState(true);
    const [conf, setConf] = React.useState({});
    
    React.useEffect(() => {
        const fetchData = async () => {
        try {
            console.log('loading HomeConf-1')
            const conf = await loadHomeConf()
            setConf(conf)
            setLoading(false);
            console.log('AppConf0: ', conf);
        } catch (error) {
            console.error('Error fetching data:', error);
            sessionStorage.removeItem("raSpa");
        }
        };
        fetchData();
    }, []);

    if (loading) {
        return <Loading loadingPrimary="Loading..." loadingSecondary="Please wait" />;
    }
        //conf = useConf();
        const dataProvider = jsonapiClient(conf.api_root, { conf: {} }, null);
