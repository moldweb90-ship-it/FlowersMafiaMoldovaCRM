<?php
/**
 * Flowers Mafia Moldova CRM -> Joomla/VirtueMart price sync endpoint.
 *
 * Install:
 * 1. Copy this file to the Joomla site root, for example:
 *    public_html/crm-price-sync.php
 * 2. Replace CHANGE_ME_WITH_LONG_RANDOM_TOKEN with the same token saved in CRM settings.
 * 3. Use this endpoint in CRM settings:
 *    https://flowersmafia.md/crm-price-sync.php
 *
 * Request:
 * POST JSON {"items":[{"sku":"ABC-123","price":1200}]}
 * Header: X-CRM-Token: your-secret-token
 */

const CRM_PRICE_SYNC_TOKEN = 'CHANGE_ME_WITH_LONG_RANDOM_TOKEN';

define('_JEXEC', 1);

if (!defined('JPATH_BASE')) {
    define('JPATH_BASE', __DIR__);
}

require_once JPATH_BASE . '/includes/defines.php';
require_once JPATH_BASE . '/includes/framework.php';

if (class_exists('\\Joomla\\CMS\\Factory')) {
    $app = \Joomla\CMS\Factory::getApplication('site');
    $db = \Joomla\CMS\Factory::getDbo();
} else {
    $app = JFactory::getApplication('site');
    $db = JFactory::getDbo();
}

header('Content-Type: application/json; charset=utf-8');

function crm_json_response(int $status, array $payload): void
{
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    crm_json_response(405, [
        'success' => false,
        'message' => 'Only POST is allowed.',
    ]);
}

$headers = function_exists('getallheaders') ? getallheaders() : [];
$token = $headers['X-CRM-Token'] ?? $headers['x-crm-token'] ?? '';

if (!hash_equals(CRM_PRICE_SYNC_TOKEN, $token)) {
    crm_json_response(401, [
        'success' => false,
        'message' => 'Invalid CRM token.',
    ]);
}

$rawBody = file_get_contents('php://input');
$payload = json_decode($rawBody, true);

if (!is_array($payload) || !isset($payload['items']) || !is_array($payload['items'])) {
    crm_json_response(400, [
        'success' => false,
        'message' => 'Invalid payload. Expected JSON with items array.',
    ]);
}

$results = [];
$updated = 0;
$notFound = 0;
$failed = 0;

foreach ($payload['items'] as $item) {
    $sku = trim((string)($item['sku'] ?? ''));
    $price = $item['price'] ?? null;

    if ($sku === '' || !is_numeric($price)) {
        $failed++;
        $results[] = [
            'sku' => $sku,
            'success' => false,
            'message' => 'Missing sku or numeric price.',
        ];
        continue;
    }

    $price = round((float)$price, 2);

    try {
        $query = $db->getQuery(true)
            ->select($db->quoteName('virtuemart_product_id'))
            ->from($db->quoteName('#__virtuemart_products'))
            ->where($db->quoteName('product_sku') . ' = ' . $db->quote($sku))
            ->setLimit(1);
        $db->setQuery($query);
        $productId = (int)$db->loadResult();

        if (!$productId) {
            $notFound++;
            $results[] = [
                'sku' => $sku,
                'success' => false,
                'message' => 'Product not found by SKU.',
            ];
            continue;
        }

        $query = $db->getQuery(true)
            ->select($db->quoteName('virtuemart_product_price_id'))
            ->from($db->quoteName('#__virtuemart_product_prices'))
            ->where($db->quoteName('virtuemart_product_id') . ' = ' . (int)$productId)
            ->order($db->quoteName('virtuemart_product_price_id') . ' ASC')
            ->setLimit(1);
        $db->setQuery($query);
        $priceId = (int)$db->loadResult();

        if (!$priceId) {
            $failed++;
            $results[] = [
                'sku' => $sku,
                'product_id' => $productId,
                'success' => false,
                'message' => 'Product price row not found.',
            ];
            continue;
        }

        $query = $db->getQuery(true)
            ->update($db->quoteName('#__virtuemart_product_prices'))
            ->set($db->quoteName('product_price') . ' = ' . $db->quote($price))
            ->where($db->quoteName('virtuemart_product_price_id') . ' = ' . (int)$priceId);
        $db->setQuery($query);
        $db->execute();

        $updated++;
        $results[] = [
            'sku' => $sku,
            'product_id' => $productId,
            'price_id' => $priceId,
            'price' => $price,
            'success' => true,
            'message' => 'Price updated.',
        ];
    } catch (Throwable $e) {
        $failed++;
        $results[] = [
            'sku' => $sku,
            'success' => false,
            'message' => $e->getMessage(),
        ];
    }
}

crm_json_response(200, [
    'success' => $failed === 0,
    'message' => "Updated: {$updated}, not found: {$notFound}, failed: {$failed}.",
    'updated' => $updated,
    'not_found' => $notFound,
    'failed' => $failed,
    'results' => $results,
]);
